"""Build the data products used by Solar Dust Advisor.

Run from the project root with ``python analysis.py``.  The script keeps the
existing financial parameters and adds measured analysis results and compact
chart arrays to both JSON locations used by the project.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
INPUT_FILES = {
    "soiling": DATA_DIR / "soiling_analyzed_data.csv",
    "merged": DATA_DIR / "merged_pv_weather_data.csv",
    "daytime": DATA_DIR / "daytime_pv_data.csv",
}
OUTPUT_FILES = (DATA_DIR / "data.json", PROJECT_ROOT / "data.json")
SCATTER_SAMPLE_SIZE = 400
PROBLEM_POWER_RATIO = 0.80
IRRADIATION_BIN_COUNT = 20


def _require_columns(frame: pd.DataFrame, columns: set[str], name: str) -> None:
    missing = columns.difference(frame.columns)
    if missing:
        raise ValueError(f"{name} is missing columns: {', '.join(sorted(missing))}")


def _pearson(frame: pd.DataFrame, left: str, right: str) -> float:
    values = frame[[left, right]].apply(pd.to_numeric, errors="coerce").dropna()
    if len(values) < 2:
        return None
    return float(values[left].corr(values[right]))


def _json_number(value):
    if value is None or not np.isfinite(value):
        return None
    return float(value)


def _records(frame: pd.DataFrame) -> list[dict]:
    return json.loads(frame.to_json(orient="records", date_format="iso"))


def _load_inputs() -> dict[str, pd.DataFrame]:
    soiling = pd.read_csv(INPUT_FILES["soiling"])
    merged = pd.read_csv(INPUT_FILES["merged"], parse_dates=["DATE_TIME"])
    daytime = pd.read_csv(INPUT_FILES["daytime"], parse_dates=["DATE_TIME"])

    _require_columns(
        soiling,
        {
            "days_since_last_cleaning",
            "gloss",
            "pm10_avg",
            "precip_avg",
            "collector_temperature",
            "wind_u_avg",
            "wind_v_avg",
            "ESTIMATED_SOILING_LOSS_PERCENT",
        },
        "soiling_analyzed_data.csv",
    )
    _require_columns(merged, {"DATE_TIME", "DC_POWER", "IRRADIATION"}, "merged_pv_weather_data.csv")
    _require_columns(
        daytime,
        {"DATE_TIME", "DC_POWER", "IRRADIATION", "MODULE_TEMPERATURE"},
        "daytime_pv_data.csv",
    )
    return {"soiling": soiling, "merged": merged, "daytime": daytime}


def _soiling_analysis(soiling: pd.DataFrame, daytime: pd.DataFrame) -> dict:
    values = soiling[
        ["days_since_last_cleaning", "ESTIMATED_SOILING_LOSS_PERCENT"]
    ].apply(pd.to_numeric, errors="coerce").dropna()
    slope, intercept = np.polyfit(
        values["days_since_last_cleaning"],
        values["ESTIMATED_SOILING_LOSS_PERCENT"],
        1,
    )
    temperature_values = daytime[
        ["MODULE_TEMPERATURE", "DC_POWER", "IRRADIATION"]
    ].apply(pd.to_numeric, errors="coerce").dropna()
    temperature_values = temperature_values[temperature_values["IRRADIATION"] >= 0.01].copy()
    temperature_values["efficiency_ratio"] = (
        temperature_values["DC_POWER"] / temperature_values["IRRADIATION"]
    )
    module_temp_regression_slope, module_temp_regression_intercept = np.polyfit(
        temperature_values["MODULE_TEMPERATURE"],
        temperature_values["efficiency_ratio"],
        1,
    )
    mean_module_temperature = temperature_values["MODULE_TEMPERATURE"].mean()
    efficiency_at_25c = (
        module_temp_regression_slope * 25 + module_temp_regression_intercept
    )
    efficiency_at_actual_temp = (
        module_temp_regression_slope * mean_module_temperature
        + module_temp_regression_intercept
    )
    temperature_loss_percent = (
        max(0.0, (efficiency_at_25c - efficiency_at_actual_temp) / efficiency_at_25c * 100)
        if efficiency_at_25c > 0
        else 0.0
    )
    gloss_values = soiling[["days_since_last_cleaning", "gloss"]].apply(
        pd.to_numeric, errors="coerce"
    ).dropna()
    gloss_slope, gloss_intercept = np.polyfit(
        gloss_values["days_since_last_cleaning"], gloss_values["gloss"], 1
    )

    precipitation = pd.to_numeric(soiling["precip_avg"], errors="coerce")
    wet = soiling[precipitation > 0]
    dry = soiling[precipitation == 0]
    climate = soiling[
        [
            "pm10_avg",
            "collector_temperature",
            "wind_u_avg",
            "wind_v_avg",
            "precip_avg",
            "ESTIMATED_SOILING_LOSS_PERCENT",
        ]
    ].apply(pd.to_numeric, errors="coerce")
    climate["wind_speed"] = np.sqrt(climate["wind_u_avg"] ** 2 + climate["wind_v_avg"] ** 2)
    climate_factor_names = {
        "pm10_avg": "تركيز الغبار (PM10)",
        "collector_temperature": "الحرارة",
        "wind_speed": "الرياح",
        "precip_avg": "المطر",
    }
    climate_correlations = [
        {
            "factor": label,
            "correlation": _json_number(
                abs(_pearson(climate, column, "ESTIMATED_SOILING_LOSS_PERCENT") or 0)
            ),
        }
        for column, label in climate_factor_names.items()
    ]
    climate_correlations.sort(key=lambda item: item["correlation"], reverse=True)
    gloss_by_days = (
        soiling.assign(
            days_approx=(
                pd.to_numeric(soiling["days_since_last_cleaning"], errors="coerce")
                .floordiv(5)
                .mul(5)
                .astype("Int64")
            )
        )
        .groupby("days_approx", dropna=True)
        .agg(
            gloss_mean=("gloss", "mean"),
            soiling_loss_percent_mean=("ESTIMATED_SOILING_LOSS_PERCENT", "mean"),
            sample_count=("gloss", "size"),
        )
        .reset_index()
        .sort_values("days_approx")
    )
    soiling_points = soiling[
        ["days_since_last_cleaning", "gloss", "ESTIMATED_SOILING_LOSS_PERCENT"]
    ].dropna()
    pm10_points = soiling[["pm10_avg", "ESTIMATED_SOILING_LOSS_PERCENT"]].dropna()
    soiling_sample = soiling_points.sample(
        n=min(SCATTER_SAMPLE_SIZE, len(soiling_points)), random_state=42
    ).sort_values("days_since_last_cleaning")
    pm10_sample = pm10_points.sample(
        n=min(SCATTER_SAMPLE_SIZE, len(pm10_points)), random_state=42
    ).sort_values("pm10_avg")

    # The old value was 33.98% / 33 days.  The regression slope is the measured
    # replacement; daily_soiling_rate below stays fractional for the web app.
    old_slope_percent_per_day = 33.98 / 33
    return {
        "soiling_sample_count": int(len(values)),
        "daily_soiling_rate_percent_per_day": _json_number(slope),
        "daily_soiling_rate": _json_number(slope / 100),
        "daily_soiling_rate_intercept": _json_number(intercept),
        "module_temp_regression_slope": _json_number(module_temp_regression_slope),
        "module_temp_regression_intercept": _json_number(module_temp_regression_intercept),
        "mean_module_temperature": _json_number(mean_module_temperature),
        "efficiency_at_25c": _json_number(efficiency_at_25c),
        "efficiency_at_actual_temp": _json_number(efficiency_at_actual_temp),
        "temperature_loss_percent": _json_number(temperature_loss_percent),
        "gloss_regression_slope": _json_number(gloss_slope),
        "gloss_regression_intercept": _json_number(gloss_intercept),
        "old_estimated_rate_percent_per_day": old_slope_percent_per_day,
        "rate_difference_percent_per_day": _json_number(slope - old_slope_percent_per_day),
        "rate_difference_relative_percent": _json_number(
            ((slope - old_slope_percent_per_day) / old_slope_percent_per_day) * 100
        ),
        "pm10_soiling_loss_pearson": _pearson(
            soiling, "pm10_avg", "ESTIMATED_SOILING_LOSS_PERCENT"
        ),
        "soiling_scatter_sample": _records(soiling_sample),
        "pm10_soiling_scatter_sample": _records(pm10_sample),
        "rain_effect": {
            "wet_definition": "precip_avg > 0",
            "dry_definition": "precip_avg == 0",
            "wet_sample_count": int(len(wet)),
            "dry_sample_count": int(len(dry)),
            "wet_mean_gloss": _json_number(wet["gloss"].mean()),
            "dry_mean_gloss": _json_number(dry["gloss"].mean()),
            "wet_mean_soiling_loss_percent": _json_number(
                wet["ESTIMATED_SOILING_LOSS_PERCENT"].mean()
            ),
            "dry_mean_soiling_loss_percent": _json_number(
                dry["ESTIMATED_SOILING_LOSS_PERCENT"].mean()
            ),
        },
        "climate_factor_correlations": climate_correlations,
        "gloss_curve": _records(gloss_by_days),
    }


def _pv_analysis(merged: pd.DataFrame, daytime: pd.DataFrame) -> dict:
    merged = merged.copy()
    merged["DATE_TIME"] = pd.to_datetime(merged["DATE_TIME"], errors="coerce")
    merged["DC_POWER"] = pd.to_numeric(merged["DC_POWER"], errors="coerce")
    merged["IRRADIATION"] = pd.to_numeric(merged["IRRADIATION"], errors="coerce")
    daytime = daytime.copy()
    daytime["DATE_TIME"] = pd.to_datetime(daytime["DATE_TIME"], errors="coerce")
    daytime["DC_POWER"] = pd.to_numeric(daytime["DC_POWER"], errors="coerce")
    daytime["IRRADIATION"] = pd.to_numeric(daytime["IRRADIATION"], errors="coerce")

    valid_merged = merged.dropna(subset=["DATE_TIME", "DC_POWER", "IRRADIATION"])
    valid_daytime = daytime.dropna(subset=["DATE_TIME", "DC_POWER", "IRRADIATION"])
    high_threshold = float(valid_merged["IRRADIATION"].median())
    timestamp_power = (
        valid_merged.groupby("DATE_TIME", as_index=False)
        .agg(
            IRRADIATION=("IRRADIATION", "mean"),
            DC_POWER=("DC_POWER", "mean"),
            inverter_count=("DC_POWER", "size"),
        )
    )
    high = timestamp_power[timestamp_power["IRRADIATION"] > high_threshold].copy()
    high["irradiation_bin"] = pd.qcut(
        high["IRRADIATION"], q=IRRADIATION_BIN_COUNT, duplicates="drop"
    )
    expected_by_bin = high.groupby("irradiation_bin", observed=True)["DC_POWER"].transform("max")
    high["expected_dc_power"] = expected_by_bin
    problem = high[high["DC_POWER"] < high["expected_dc_power"] * PROBLEM_POWER_RATIO].copy()

    problem_columns = [
        "DATE_TIME",
        "DC_POWER",
        "IRRADIATION",
        "expected_dc_power",
        "inverter_count",
    ]
    problems = problem[problem_columns].sort_values("DATE_TIME").copy()
    problems["power_ratio_to_bin_max"] = problems["DC_POWER"] / problems["expected_dc_power"]

    daily = (
        valid_merged.assign(date=valid_merged["DATE_TIME"].dt.strftime("%Y-%m-%d"))
        .groupby("date", as_index=False)
        .agg(daily_average_dc_power=("DC_POWER", "mean"), sample_count=("DC_POWER", "size"))
    )
    scatter = valid_merged[["DATE_TIME", "IRRADIATION", "DC_POWER"]].sample(
        n=min(SCATTER_SAMPLE_SIZE, len(valid_merged)), random_state=42
    ).sort_values("IRRADIATION")

    return {
        "merged_irradiation_dc_pearson": _pearson(valid_merged, "IRRADIATION", "DC_POWER"),
        "daytime_irradiation_dc_pearson": _pearson(valid_daytime, "IRRADIATION", "DC_POWER"),
        "problem_definition": {
            "irradiation_condition": "IRRADIATION > merged median",
            "power_condition": f"DC_POWER < {PROBLEM_POWER_RATIO:.0%} of max DC_POWER in the same irradiation quantile bin",
            "irradiation_median": high_threshold,
            "power_ratio_threshold": PROBLEM_POWER_RATIO,
            "irradiation_quantile_bins": IRRADIATION_BIN_COUNT,
        },
        "problem_cases": _records(problems),
        "problem_case_count": int(len(problems)),
        "daily_average_dc_power": _records(daily),
        "irradiation_dc_power_scatter_sample": _records(scatter),
    }


def _base_payload() -> dict:
    source = PROJECT_ROOT / "data.json"
    if source.exists():
        with source.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    else:
        payload = {}
    payload.setdefault("psh", None)
    payload.setdefault("pr", None)
    payload.setdefault("cleaning_cost_per_kw_iqd", None)
    payload.setdefault("default_tariff_iqd", None)
    payload.setdefault("payback_threshold_days", None)
    payload.setdefault("baseline_gloss", None)
    payload.setdefault(
        "defaults",
        {
            "capacity_kw": 100,
            "tariff_iqd_per_kwh": 200,
            "cleaning_cost_iqd": 240000,
            "last_cleaning_date": "2026-08-15",
        },
    )
    return payload


def build_payload(frames: dict[str, pd.DataFrame]) -> dict:
    soiling_result = _soiling_analysis(frames["soiling"], frames["daytime"])
    pv_result = _pv_analysis(frames["merged"], frames["daytime"])
    soiling = frames["soiling"]
    merged = frames["merged"]
    payload = _base_payload()
    payload["daily_soiling_rate"] = soiling_result["daily_soiling_rate"]
    payload["daily_soiling_rate_source"] = (
        "انحدار خطي فعلي بين days_since_last_cleaning و "
        "ESTIMATED_SOILING_LOSS_PERCENT؛ القيمة في الحقل كسر عشري"
    )
    payload["temp_loss_percent"] = soiling_result["temperature_loss_percent"]
    payload["temp_loss_percent_source"] = (
        "انحدار خطي فعلي بين MODULE_TEMPERATURE و efficiency_ratio="
        "DC_POWER/IRRADIATION من daytime_pv_data.csv؛ مقارنة الكفاءة عند 25°م "
        "بكفاءتها عند متوسط الحرارة الفعلية"
    )
    payload["analysis"] = {
        **soiling_result,
        **pv_result,
        "period_start": merged["DATE_TIME"].min().strftime("%Y-%m-%d"),
        "period_end": merged["DATE_TIME"].max().strftime("%Y-%m-%d"),
        "average_soiling_loss_percent": _json_number(soiling["ESTIMATED_SOILING_LOSS_PERCENT"].mean()),
        "maximum_soiling_loss_percent": _json_number(soiling["ESTIMATED_SOILING_LOSS_PERCENT"].max()),
        "average_temperature_c": _json_number(merged["AMBIENT_TEMPERATURE"].mean())
        if "AMBIENT_TEMPERATURE" in merged
        else None,
        "average_solar_irradiation": _json_number(merged["IRRADIATION"].mean()),
    }
    return payload


def main() -> None:
    payload = build_payload(_load_inputs())
    serialized = json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    for output in OUTPUT_FILES:
        output.write_text(serialized, encoding="utf-8")
    rate = payload["analysis"]["daily_soiling_rate_percent_per_day"]
    print(f"Wrote {len(serialized):,} bytes to {', '.join(str(path) for path in OUTPUT_FILES)}")
    print(f"Measured daily soiling rate: {rate:.6f}% loss/day ({rate / 100:.8f} fraction/day)")
    print(f"Problem cases: {payload['analysis']['problem_case_count']}")


if __name__ == "__main__":
    main()