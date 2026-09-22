PANEL_CAPACITY_KW = 0.5
WATER_COST_PER_PANEL_IQD = 500
LABOR_COST_PER_PANEL_IQD = 600
CONSUMABLES_PER_PANEL_IQD = 100
DEFAULT_TARIFF_IQD_PER_KWH = 200
PAYBACK_CLEAN_THRESHOLD_DAYS = 15
PAYBACK_NO_CLEAN_THRESHOLD_DAYS = 30
FORECAST_DAYS = 14
IGNORE_DAYS = 30
WEEKS_TO_FORECAST = 4


def calculate_default_cleaning_cost(capacity_kw):
    num_panels = capacity_kw / PANEL_CAPACITY_KW
    cleaning_cost_per_panel = (
        WATER_COST_PER_PANEL_IQD
        + LABOR_COST_PER_PANEL_IQD
        + CONSUMABLES_PER_PANEL_IQD
    )
    return num_panels * cleaning_cost_per_panel


def calculate_metrics(capacity_kw, tariff, cleaning_cost, analysis):
    dust_loss_pct = analysis["maximum_soiling_loss_percent"]
    num_panels = capacity_kw / PANEL_CAPACITY_KW
    cleaning_cost_per_panel = (
        WATER_COST_PER_PANEL_IQD
        + LABOR_COST_PER_PANEL_IQD
        + CONSUMABLES_PER_PANEL_IQD
    )
    sun_hours = analysis["average_solar_irradiation"]
    total_potential_kwh_daily = capacity_kw * sun_hours
    lost_energy_kwh_daily = total_potential_kwh_daily * (dust_loss_pct / 100)
    daily_financial_loss_iqd = lost_energy_kwh_daily * tariff
    weekly_loss_iqd = daily_financial_loss_iqd * 7
    payback_days = cleaning_cost / daily_financial_loss_iqd if daily_financial_loss_iqd else float("inf")
    if payback_days < PAYBACK_CLEAN_THRESHOLD_DAYS:
        recommendation = "Clean Today"
    elif payback_days > PAYBACK_NO_CLEAN_THRESHOLD_DAYS:
        recommendation = "Do Not Clean"
    else:
        recommendation = "Consider Cleaning"

    return {
        "num_panels": num_panels,
        "cleaning_cost_per_panel": cleaning_cost_per_panel,
        "calculated_cleaning_cost_iqd": num_panels * cleaning_cost_per_panel,
        "total_cleaning_cost_iqd": cleaning_cost,
        "sun_hours": sun_hours,
        "total_potential_kwh_daily": total_potential_kwh_daily,
        "lost_energy_kwh_daily": lost_energy_kwh_daily,
        "dust_loss_pct": dust_loss_pct,
        "daily_financial_loss_iqd": daily_financial_loss_iqd,
        "weekly_loss_iqd": weekly_loss_iqd,
        "payback_days": payback_days,
        "recommendation": recommendation,
    }


def build_forecast(metrics):
    start_loss = metrics["dust_loss_pct"]
    return [
        round(max(0, 100 - start_loss * (1 + day / FORECAST_DAYS)), 2)
        for day in range(FORECAST_DAYS)
    ]


def build_cumulative_loss(metrics):
    daily_accumulation_rate = metrics["daily_financial_loss_iqd"]
    return [
        round(daily_accumulation_rate * day, 2)
        for day in range(1, FORECAST_DAYS + 1)
    ]


def build_weekly_losses(metrics):
    daily_accumulation_rate = metrics["daily_financial_loss_iqd"]
    return [
        round(daily_accumulation_rate * 7 * week, 2)
        for week in range(1, WEEKS_TO_FORECAST + 1)
    ]


def build_scenarios(capacity_kw, tariff, cleaning_cost, analysis, metrics):
    baseline_daily_revenue = capacity_kw * analysis["average_solar_irradiation"] * tariff
    clean_daily_revenue = baseline_daily_revenue
    ignored_daily_revenue = baseline_daily_revenue * (1 - metrics["dust_loss_pct"] / 100)
    clean_net_revenue = clean_daily_revenue * IGNORE_DAYS - cleaning_cost
    ignored_revenue = ignored_daily_revenue * IGNORE_DAYS
    return {
        "clean_revenue": clean_net_revenue,
        "ignore_revenue": ignored_revenue,
        "clean_efficiency": "100% after cleaning",
        "ignore_efficiency": f"{max(0, 100 - metrics['dust_loss_pct']):.1f}% average",
    }
