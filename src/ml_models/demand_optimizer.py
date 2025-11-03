"""
Demand Forecasting and Inventory Optimization Module

Este módulo combina:
1. Modelos predictivos de demanda (ARIMA + Random Forest)
2. Análisis de estacionalidad y eventos especiales
3. Optimización de niveles de stock
4. Sistema de reabastecimiento inteligente

Objetivo: Reducir quiebres de stock sin sobrestock, optimizando pedidos a proveedores.
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import TimeSeriesSplit
from statsmodels.tsa.statespace.sarimax import SARIMAX

from src.utils.load_data import ensure_directory


@dataclass
class DemandForecast:
    """Resultado de predicción de demanda para un producto/categoría."""
    producto_id: str
    nombre: str
    categoria: str
    fecha_inicio: datetime
    dias_forecast: int
    demanda_diaria: List[float]  # Predicción de demanda por día
    demanda_lower: List[float]   # Intervalo de confianza inferior
    demanda_upper: List[float]   # Intervalo de confianza superior
    modelo_usado: str            # 'arima', 'random_forest', 'ensemble'
    metricas: Dict[str, float]   # MAE, RMSE, etc.
    estacionalidad: Dict[str, float]  # Factores estacionales detectados


@dataclass
class ReorderRecommendation:
    """Recomendación de reabastecimiento para un producto."""
    producto_id: str
    nombre: str
    categoria: str
    stock_actual: float
    stock_optimo: float
    punto_reorden: float
    cantidad_pedir: float
    dias_hasta_agotamiento: float
    urgencia: str  # 'critico', 'urgente', 'normal', 'ok'
    costo_estimado: float
    demanda_semanal_estimada: float
    lead_time_dias: int = 7  # Días que tarda el proveedor


class DemandOptimizer:
    """
    Optimizador de demanda e inventarios con múltiples modelos predictivos.
    """

    def __init__(
        self,
        ventas_df: pd.DataFrame,
        productos_df: Optional[pd.DataFrame] = None,
        stock_df: Optional[pd.DataFrame] = None,
    ):
        """
        Args:
            ventas_df: DataFrame con columnas [fecha, producto_id, categoria, cantidad, monto]
            productos_df: DataFrame con info de productos [producto_id, nombre, categoria, costo]
            stock_df: DataFrame con stock actual [producto_id, stock_actual]
        """
        self.ventas_df = ventas_df.copy()
        self.productos_df = productos_df.copy() if productos_df is not None else None
        self.stock_df = stock_df.copy() if stock_df is not None else None

        # Asegurar que fecha es datetime
        if 'fecha' in self.ventas_df.columns:
            self.ventas_df['fecha'] = pd.to_datetime(self.ventas_df['fecha'])

        # Modelos entrenados
        self.arima_models: Dict[str, SARIMAX] = {}
        self.rf_models: Dict[str, RandomForestRegressor] = {}
        self.seasonality_factors: Dict[str, Dict[str, float]] = {}

    def _prepare_time_series(
        self,
        producto_id: str,
        min_observations: int = 30
    ) -> Optional[pd.Series]:
        """Prepara serie temporal de demanda diaria para un producto."""
        producto_ventas = self.ventas_df[
            self.ventas_df['producto_id'] == producto_id
        ].copy()

        if len(producto_ventas) < min_observations:
            return None

        # Agregar por fecha
        daily_demand = producto_ventas.groupby('fecha')['cantidad'].sum()

        # Rellenar fechas faltantes con 0 (no hubo ventas)
        date_range = pd.date_range(
            start=daily_demand.index.min(),
            end=daily_demand.index.max(),
            freq='D'
        )
        daily_demand = daily_demand.reindex(date_range, fill_value=0)

        return daily_demand

    def _detect_seasonality(self, series: pd.Series) -> Dict[str, float]:
        """
        Detecta patrones estacionales en la serie temporal.

        Returns:
            Dict con factores estacionales por día de semana y fin de semana.
        """
        df = pd.DataFrame({'demanda': series})
        df['dia_semana'] = df.index.dayofweek  # 0=Lunes, 6=Domingo
        df['es_fin_semana'] = df['dia_semana'].isin([5, 6]).astype(int)

        # Factor por día de semana (relativo al promedio)
        promedio_general = df['demanda'].mean()
        if promedio_general == 0:
            promedio_general = 1  # Evitar división por cero

        factores_dia = {}
        for dia in range(7):
            promedio_dia = df[df['dia_semana'] == dia]['demanda'].mean()
            factores_dia[f'dia_{dia}'] = promedio_dia / promedio_general

        # Factor fin de semana vs entre semana
        promedio_finde = df[df['es_fin_semana'] == 1]['demanda'].mean()
        promedio_semana = df[df['es_fin_semana'] == 0]['demanda'].mean()

        factores_dia['fin_semana'] = promedio_finde / promedio_general if promedio_general > 0 else 1.0
        factores_dia['entre_semana'] = promedio_semana / promedio_general if promedio_general > 0 else 1.0

        return factores_dia

    def _create_features_for_rf(self, series: pd.Series) -> pd.DataFrame:
        """
        Crea features para Random Forest basadas en la serie temporal.

        Features incluyen:
        - Lags (1, 7, 14, 30 días)
        - Rolling means (7, 14, 30 días)
        - Día de semana, día del mes
        - Es fin de semana
        - Tendencia (día número)
        """
        df = pd.DataFrame({'demanda': series})
        df['fecha'] = df.index

        # Features temporales
        df['dia_semana'] = df.index.dayofweek
        df['dia_mes'] = df.index.day
        df['mes'] = df.index.month
        df['es_fin_semana'] = df['dia_semana'].isin([5, 6]).astype(int)
        df['dia_numero'] = (df.index - df.index.min()).days

        # Lags
        for lag in [1, 7, 14, 30]:
            df[f'lag_{lag}'] = df['demanda'].shift(lag)

        # Rolling statistics
        for window in [7, 14, 30]:
            df[f'rolling_mean_{window}'] = df['demanda'].rolling(window).mean()
            df[f'rolling_std_{window}'] = df['demanda'].rolling(window).std()

        # Llenar NaNs con forward fill y luego con 0
        df = df.fillna(method='bfill').fillna(0)

        return df

    def _train_arima_model(
        self,
        series: pd.Series,
        order: Tuple[int, int, int] = None
    ) -> Tuple[SARIMAX, float]:
        """
        Entrena modelo ARIMA para la serie temporal.

        Returns:
            Modelo entrenado y su AIC score.
        """
        if order is None:
            # Grid search simple para encontrar mejor orden
            best_aic = np.inf
            best_order = (1, 1, 1)
            best_model = None

            for p in [0, 1, 2]:
                for d in [0, 1]:
                    for q in [0, 1, 2]:
                        try:
                            with warnings.catch_warnings():
                                warnings.simplefilter("ignore")
                                model = SARIMAX(
                                    series,
                                    order=(p, d, q),
                                    enforce_stationarity=False,
                                    enforce_invertibility=False,
                                )
                                fitted = model.fit(disp=False)

                            if fitted.aic < best_aic:
                                best_aic = fitted.aic
                                best_order = (p, d, q)
                                best_model = fitted
                        except:
                            continue

            return best_model, best_aic
        else:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                model = SARIMAX(
                    series,
                    order=order,
                    enforce_stationarity=False,
                    enforce_invertibility=False,
                )
                fitted = model.fit(disp=False)
            return fitted, fitted.aic

    def _train_random_forest(
        self,
        df_features: pd.DataFrame,
        test_size: int = 30
    ) -> Tuple[RandomForestRegressor, float]:
        """
        Entrena Random Forest con validación temporal.

        Returns:
            Modelo entrenado y MAE en set de validación.
        """
        # Features excluyen la columna target y fecha
        feature_cols = [col for col in df_features.columns
                       if col not in ['demanda', 'fecha']]

        X = df_features[feature_cols].values
        y = df_features['demanda'].values

        # Split temporal: últimos test_size días para validación
        X_train, X_test = X[:-test_size], X[-test_size:]
        y_train, y_test = y[:-test_size], y[-test_size:]

        # Entrenar Random Forest
        rf = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            random_state=42,
            n_jobs=-1
        )
        rf.fit(X_train, y_train)

        # Evaluar
        y_pred = rf.predict(X_test)
        mae = np.mean(np.abs(y_test - y_pred))

        return rf, mae

    def forecast_demand(
        self,
        producto_id: str,
        dias_adelante: int = 30,
        modelo: str = 'ensemble'
    ) -> Optional[DemandForecast]:
        """
        Predice demanda futura para un producto.

        Args:
            producto_id: ID del producto
            dias_adelante: Días a predecir
            modelo: 'arima', 'random_forest', o 'ensemble' (combina ambos)

        Returns:
            DemandForecast con predicciones y métricas.
        """
        # Preparar serie temporal
        series = self._prepare_time_series(producto_id)
        if series is None or len(series) < 30:
            return None

        # Detectar estacionalidad
        seasonality = self._detect_seasonality(series)
        self.seasonality_factors[producto_id] = seasonality

        # Obtener info del producto
        nombre = producto_id
        categoria = "Unknown"
        if self.productos_df is not None:
            prod_info = self.productos_df[
                self.productos_df['producto_id'] == producto_id
            ]
            if not prod_info.empty:
                nombre = prod_info.iloc[0]['nombre']
                categoria = prod_info.iloc[0]['categoria']

        predictions = []
        lower_bounds = []
        upper_bounds = []
        metricas = {}

        # Predicción con ARIMA
        if modelo in ['arima', 'ensemble']:
            try:
                arima_model, aic = self._train_arima_model(series)
                self.arima_models[producto_id] = arima_model

                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    forecast_result = arima_model.get_forecast(steps=dias_adelante)

                arima_pred = forecast_result.predicted_mean.values
                conf_int = forecast_result.conf_int(alpha=0.2)
                arima_lower = conf_int.iloc[:, 0].values
                arima_upper = conf_int.iloc[:, 1].values

                predictions.append(arima_pred)
                lower_bounds.append(arima_lower)
                upper_bounds.append(arima_upper)
                metricas['arima_aic'] = aic
            except Exception as e:
                if modelo == 'arima':
                    return None
                # Si es ensemble, continuar con RF

        # Predicción con Random Forest
        if modelo in ['random_forest', 'ensemble']:
            try:
                df_features = self._create_features_for_rf(series)
                rf_model, mae = self._train_random_forest(df_features)
                self.rf_models[producto_id] = rf_model

                # Generar predicciones iterativas
                rf_pred = []
                last_features = df_features.iloc[-1:].copy()

                for _ in range(dias_adelante):
                    feature_cols = [col for col in last_features.columns
                                  if col not in ['demanda', 'fecha']]
                    pred = rf_model.predict(last_features[feature_cols].values)[0]
                    pred = max(0, pred)  # No puede ser negativa
                    rf_pred.append(pred)

                    # Actualizar features para siguiente predicción
                    # (simplificado: sólo actualizamos lags principales)
                    last_features['lag_1'] = pred
                    last_features['dia_numero'] += 1

                rf_pred = np.array(rf_pred)
                predictions.append(rf_pred)

                # Intervalo de confianza basado en MAE
                lower_bounds.append(rf_pred - 1.96 * mae)
                upper_bounds.append(rf_pred + 1.96 * mae)
                metricas['rf_mae'] = mae
            except Exception as e:
                if modelo == 'random_forest':
                    return None

        # Combinar predicciones si es ensemble
        if len(predictions) == 0:
            return None

        if modelo == 'ensemble' and len(predictions) == 2:
            # Promedio ponderado: 40% ARIMA, 60% RF (RF suele ser más robusto)
            final_pred = 0.4 * predictions[0] + 0.6 * predictions[1]
            final_lower = 0.4 * lower_bounds[0] + 0.6 * lower_bounds[1]
            final_upper = 0.4 * upper_bounds[0] + 0.6 * upper_bounds[1]
        else:
            final_pred = predictions[0]
            final_lower = lower_bounds[0]
            final_upper = upper_bounds[0]

        # Asegurar no negativos
        final_pred = np.maximum(final_pred, 0)
        final_lower = np.maximum(final_lower, 0)
        final_upper = np.maximum(final_upper, 0)

        fecha_inicio = series.index.max() + timedelta(days=1)

        return DemandForecast(
            producto_id=producto_id,
            nombre=nombre,
            categoria=categoria,
            fecha_inicio=fecha_inicio,
            dias_forecast=dias_adelante,
            demanda_diaria=final_pred.tolist(),
            demanda_lower=final_lower.tolist(),
            demanda_upper=final_upper.tolist(),
            modelo_usado=modelo,
            metricas=metricas,
            estacionalidad=seasonality
        )

    def calculate_reorder_point(
        self,
        producto_id: str,
        service_level: float = 0.95,
        lead_time_dias: int = 7
    ) -> Optional[ReorderRecommendation]:
        """
        Calcula punto de reorden óptimo y genera recomendación.

        Args:
            producto_id: ID del producto
            service_level: Nivel de servicio deseado (0.95 = 95%)
            lead_time_dias: Días que tarda el proveedor en entregar

        Returns:
            ReorderRecommendation con cantidades óptimas a pedir.
        """
        # Obtener forecast
        forecast = self.forecast_demand(producto_id, dias_adelante=lead_time_dias * 2)
        if forecast is None:
            return None

        # Demanda durante lead time
        demanda_lead_time = sum(forecast.demanda_diaria[:lead_time_dias])

        # Desviación estándar de demanda diaria (aproximada)
        std_demanda = np.std(forecast.demanda_diaria)

        # Z-score para nivel de servicio
        from scipy import stats
        z_score = stats.norm.ppf(service_level)

        # Stock de seguridad
        safety_stock = z_score * std_demanda * np.sqrt(lead_time_dias)

        # Punto de reorden = Demanda durante lead time + Stock de seguridad
        reorder_point = demanda_lead_time + safety_stock

        # Demanda semanal estimada
        demanda_semanal = sum(forecast.demanda_diaria[:7])

        # Stock óptimo (2 semanas de demanda + safety stock)
        stock_optimo = demanda_semanal * 2 + safety_stock

        # Stock actual
        stock_actual = 0
        if self.stock_df is not None:
            stock_row = self.stock_df[self.stock_df['producto_id'] == producto_id]
            if not stock_row.empty:
                stock_actual = stock_row.iloc[0]['stock_actual']

        # Cantidad a pedir
        cantidad_pedir = max(0, stock_optimo - stock_actual)

        # Días hasta agotamiento
        if demanda_semanal > 0:
            dias_hasta_agotamiento = stock_actual / (demanda_semanal / 7)
        else:
            dias_hasta_agotamiento = 999  # Infinito efectivamente

        # Determinar urgencia
        if dias_hasta_agotamiento <= lead_time_dias:
            urgencia = 'critico'
        elif dias_hasta_agotamiento <= lead_time_dias * 1.5:
            urgencia = 'urgente'
        elif stock_actual < reorder_point:
            urgencia = 'normal'
        else:
            urgencia = 'ok'

        # Costo estimado
        costo_estimado = 0
        if self.productos_df is not None:
            prod_info = self.productos_df[
                self.productos_df['producto_id'] == producto_id
            ]
            if not prod_info.empty and 'costo' in prod_info.columns:
                costo_estimado = cantidad_pedir * prod_info.iloc[0]['costo']

        return ReorderRecommendation(
            producto_id=producto_id,
            nombre=forecast.nombre,
            categoria=forecast.categoria,
            stock_actual=stock_actual,
            stock_optimo=stock_optimo,
            punto_reorden=reorder_point,
            cantidad_pedir=cantidad_pedir,
            dias_hasta_agotamiento=dias_hasta_agotamiento,
            urgencia=urgencia,
            costo_estimado=costo_estimado,
            demanda_semanal_estimada=demanda_semanal,
            lead_time_dias=lead_time_dias
        )

    def generate_reorder_report(
        self,
        output_path: Optional[Path] = None,
        top_n_productos: int = 100
    ) -> pd.DataFrame:
        """
        Genera reporte completo de reabastecimiento para los top N productos.

        Returns:
            DataFrame con recomendaciones de reorden para todos los productos.
        """
        # Obtener top productos por volumen de ventas
        top_productos = (
            self.ventas_df.groupby('producto_id')['cantidad']
            .sum()
            .nlargest(top_n_productos)
            .index.tolist()
        )

        recomendaciones = []
        for producto_id in top_productos:
            rec = self.calculate_reorder_point(producto_id)
            if rec is not None:
                recomendaciones.append({
                    'producto_id': rec.producto_id,
                    'nombre': rec.nombre,
                    'categoria': rec.categoria,
                    'stock_actual': rec.stock_actual,
                    'stock_optimo': rec.stock_optimo,
                    'punto_reorden': rec.punto_reorden,
                    'cantidad_pedir': rec.cantidad_pedir,
                    'dias_hasta_agotamiento': rec.dias_hasta_agotamiento,
                    'urgencia': rec.urgencia,
                    'costo_estimado': rec.costo_estimado,
                    'demanda_semanal_estimada': rec.demanda_semanal_estimada,
                })

        df_report = pd.DataFrame(recomendaciones)

        # Ordenar por urgencia y días hasta agotamiento
        urgencia_order = {'critico': 0, 'urgente': 1, 'normal': 2, 'ok': 3}
        df_report['urgencia_num'] = df_report['urgencia'].map(urgencia_order)
        df_report = df_report.sort_values(['urgencia_num', 'dias_hasta_agotamiento'])
        df_report = df_report.drop(columns=['urgencia_num'])

        if output_path is not None:
            ensure_directory(output_path.parent)
            df_report.to_parquet(output_path, index=False)

        return df_report


def generate_demand_forecasts_batch(
    ventas_df: pd.DataFrame,
    productos_df: Optional[pd.DataFrame] = None,
    output_dir: Optional[Path] = None,
    top_n: int = 50,
    dias_forecast: int = 30
) -> pd.DataFrame:
    """
    Genera forecasts de demanda para múltiples productos en batch.

    Args:
        ventas_df: DataFrame de ventas históricas
        productos_df: Info adicional de productos
        output_dir: Directorio donde guardar resultados
        top_n: Cantidad de productos top a procesar
        dias_forecast: Días a predecir

    Returns:
        DataFrame consolidado con todos los forecasts.
    """
    optimizer = DemandOptimizer(ventas_df, productos_df)

    # Top productos por volumen
    top_productos = (
        ventas_df.groupby('producto_id')['cantidad']
        .sum()
        .nlargest(top_n)
        .index.tolist()
    )

    all_forecasts = []

    for producto_id in top_productos:
        forecast = optimizer.forecast_demand(
            producto_id,
            dias_adelante=dias_forecast,
            modelo='ensemble'
        )

        if forecast is not None:
            # Convertir a DataFrame
            for i, (demanda, lower, upper) in enumerate(zip(
                forecast.demanda_diaria,
                forecast.demanda_lower,
                forecast.demanda_upper
            )):
                fecha = forecast.fecha_inicio + timedelta(days=i)
                all_forecasts.append({
                    'producto_id': forecast.producto_id,
                    'nombre': forecast.nombre,
                    'categoria': forecast.categoria,
                    'fecha': fecha,
                    'demanda_predicha': demanda,
                    'demanda_lower': lower,
                    'demanda_upper': upper,
                    'modelo': forecast.modelo_usado,
                })

    df_forecasts = pd.DataFrame(all_forecasts)

    if output_dir is not None:
        ensure_directory(output_dir)
        output_path = output_dir / 'demand_forecasts.parquet'
        df_forecasts.to_parquet(output_path, index=False)

    return df_forecasts
