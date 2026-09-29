"""
Energy, land and investment needed to move the Philippine aviation sector to
DAC-based e-kerosene. This is a Python version of "SAF Calculations.xlsx", used
to cross-check the spreadsheet and to generate the data for the web demo.

Usage:
    pip install openpyxl
    python analysis/saf_model.py
"""
from dataclasses import dataclass, asdict
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "data" / "saf_model.json"


@dataclass
class Inputs:
    # Demand
    jet_fuel_bbl_per_day: float = 33_700      # Philippine aviation fuel use
    litres_per_hour_per_bbl_day: float = 4.9  # conversion used in the spreadsheet
    # Fuel production (Seymour et al., 2024)
    efuel_blend_kwh_per_litre: float = 25.2   # energy to produce the e-fuel blend
    kerosene_fraction: float = 0.4            # litres of e-kerosene per litre of blend
    # Renewable supply
    capacity_factor_solar: float = 0.2
    capacity_factor_wind: float = 0.3
    re_goal_2040_gw: float = 20.0             # national renewable capacity goal for 2040
    # Land (Bolinger et al., 2022; NREL)
    solar_mw_per_ha: float = 0.87
    wind_ha_per_mw: float = 34.0
    panels_per_mw: tuple = (2_200, 2_800)
    turbine_mw: tuple = (2.0, 3.0)
    # Costs (Sens et al., 2022), EUR
    solar_capex_eur_per_kw: dict = None
    wind_capex_eur_per_kw: dict = None
    efuel_plant_capex_eur_per_litre: dict = None  # per litre of annual output
    efuel_opex_share: float = 0.195               # annual OPEX as a share of plant CAPEX

    def __post_init__(self):
        self.solar_capex_eur_per_kw = self.solar_capex_eur_per_kw or {2030: 430, 2050: 330}
        self.wind_capex_eur_per_kw = self.wind_capex_eur_per_kw or {2030: 1210, 2050: 970}
        self.efuel_plant_capex_eur_per_litre = self.efuel_plant_capex_eur_per_litre or {2030: 0.85, 2050: 0.45}


def run(p: Inputs) -> dict:
    kwh_per_litre = p.efuel_blend_kwh_per_litre * p.kerosene_fraction   # e-kerosene via DAC
    litres_per_hour = p.jet_fuel_bbl_per_day * p.litres_per_hour_per_bbl_day
    power_mw = kwh_per_litre * litres_per_hour / 1000                    # continuous electrical load

    solar_mw = power_mw / p.capacity_factor_solar
    wind_mw = power_mw / p.capacity_factor_wind

    litres_per_year = litres_per_hour * 8760
    capex = {}
    for year in (2030, 2050):
        plant = p.efuel_plant_capex_eur_per_litre[year] * litres_per_year
        capex[year] = {
            "solar_plants": solar_mw * 1000 * p.solar_capex_eur_per_kw[year],
            "wind_plants": wind_mw * 1000 * p.wind_capex_eur_per_kw[year],
            "efuel_plant": plant,
            "efuel_opex_per_year": plant * p.efuel_opex_share,
        }
        capex[year]["total_solar_route"] = capex[year]["solar_plants"] + plant
        capex[year]["total_wind_route"] = capex[year]["wind_plants"] + plant

    return {
        "energy_kwh_per_litre": kwh_per_litre,
        "fuel_litres_per_hour": litres_per_hour,
        "power_mw": power_mw,
        "solar_mw": solar_mw,
        "wind_mw": wind_mw,
        "share_of_2040_goal": {"solar": solar_mw / (p.re_goal_2040_gw * 1000), "wind": wind_mw / (p.re_goal_2040_gw * 1000)},
        "land_ha": {"solar": solar_mw / p.solar_mw_per_ha, "wind": wind_mw * p.wind_ha_per_mw},
        "solar_panels": [solar_mw * n for n in p.panels_per_mw],
        "wind_turbines": [wind_mw / mw for mw in reversed(p.turbine_mw)],
        "capex_eur": capex,
    }


def check_against_spreadsheet(result: dict) -> None:
    """Compare with the values calculated in SAF Calculations.xlsx."""
    try:
        from openpyxl import load_workbook
    except ImportError:
        print("openpyxl not installed, skipping spreadsheet check")
        return
    ws = load_workbook(ROOT / "SAF Calculations.xlsx", data_only=True).active
    pairs = {
        "power_mw": ws["B10"].value,
        "solar_mw": ws["B26"].value,
        "wind_mw": ws["B27"].value,
        "land solar": (result["land_ha"]["solar"], ws["B33"].value),
        "land wind": (result["land_ha"]["wind"], ws["B39"].value),
        "solar CAPEX 2030": (result["capex_eur"][2030]["solar_plants"], ws["B44"].value),
        "wind CAPEX 2030": (result["capex_eur"][2030]["wind_plants"], ws["B45"].value),
        "e-fuel CAPEX 2030": (result["capex_eur"][2030]["efuel_plant"], ws["B46"].value),
        "e-fuel CAPEX 2050": (result["capex_eur"][2050]["efuel_plant"], ws["C46"].value),
    }
    for name, expected in pairs.items():
        got, want = expected if isinstance(expected, tuple) else (result[name], expected)
        assert abs(got - want) / want < 0.005, f"{name}: {got:,.0f} != {want:,.0f}"
    print("Matches SAF Calculations.xlsx: OK")


def main() -> None:
    inputs = Inputs()
    r = run(inputs)
    check_against_spreadsheet(r)

    print(f"Continuous power for e-kerosene: {r['power_mw']:,.0f} MW")
    print(f"Installed capacity: {r['solar_mw']:,.0f} MW solar or {r['wind_mw']:,.0f} MW wind")
    print(f"Land: {r['land_ha']['solar']:,.0f} ha (solar) vs {r['land_ha']['wind']:,.0f} ha (wind)")
    for year in (2030, 2050):
        c = r["capex_eur"][year]
        print(f"CAPEX {year}: €{c['total_solar_route'] / 1e9:.1f}B (solar) to €{c['total_wind_route'] / 1e9:.1f}B (wind)")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"inputs": asdict(inputs), "results": r}, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
