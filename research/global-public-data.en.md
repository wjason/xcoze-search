# Global public data sources

[简体中文](global-public-data.md) | **English**

[Back to sources](../references/sources.en.md)

This page tracks public data that may help Agents answer questions. An accessible endpoint, useful content, and an integrated adapter are different things. Check each provider's terms, update frequency, coverage, and content license.

## Integrated

| Source | Capability | Notes |
|---|---|---|
| [NASA media library](https://api.nasa.gov/) | Search image, video, and audio titles, descriptions, and creation times | Returns media metadata; media is not downloaded. Individual assets have their own usage conditions. |
| [U.S. Federal Register](https://www.federalregister.gov/developers/documentation/api/v1) | Search federal notices and abstracts | Publication and effective dates are different; consult the original document. |
| [World Bank](https://datahelpdesk.worldbank.org/knowledgebase/articles/889392) | Look up economic and social indicators by country and indicator code | Annual observations can be missing or revised and are not live stock quotes. Confirm both codes first. |
| [USGS earthquake feeds](https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php) | Retrieve recent earthquake magnitudes, locations, and event times | Results may be revised. Coverage depends on the selected feed; event times are UTC. |

On 2026-11-05, each of these four paths returned results in a single keyless xcoze search check. One success does not guarantee future availability or access from every network.

```bash
python3 scripts/xcoze_search.py search 'james webb' --platform nasa --strategy free
python3 scripts/xcoze_search.py search 'renewable energy' --platform federalregister --strategy free
python3 scripts/xcoze_search.py search 'CN,SP.POP.TOTL' --platform worldbank --strategy free
python3 scripts/xcoze_search.py search '2.5,day' --platform usgs --strategy free
```

The World Bank example selects China's population indicator; it does not map natural-language questions to indicators. USGS supports combinations of `all`, `significant`, `1.0`, `2.5`, `4.5` and `hour`, `day`, `week`, `month`. For example, `2.5,day` selects the feed for magnitude 2.5 and above over the past day. Arbitrary historical and geographic filters are not integrated.

## Weather and the environment

| Source | Data | Status |
|---|---|---|
| [MET Norway](https://api.met.no/weatherapi/locationforecast/2.0/documentation) | Global coordinate-based forecasts | Keyless Beijing sample returned data. Integration needs response-header caching, coordinate precision, and attribution; forecasts are not observations. |
| [Open-Meteo](https://open-meteo.com/en/docs) | Geocoding and forecasts | Keyless samples returned data; its [free API is for non-commercial use](https://open-meteo.com/en/terms), and commercial use requires an appropriate license. Not integrated. |
| [NOAA Space Weather](https://www.swpc.noaa.gov/products-and-data) | Solar and space-weather products | A public JSON sample responded; fields, time semantics and integration need review. |
| [USGS earthquakes](https://earthquake.usgs.gov/earthquakes/feed/v1.0/index.php) | Earthquake events | Fixed recent feeds are integrated; the full catalog API is not. |

Weather queries may require coordinates and disambiguation of place names. Location, forecast update time, and source affect results. These services do not replace local authorities' hazard warnings.

## Stocks, finance, and economics

| Source | Data | Status |
|---|---|---|
| [U.S. SEC EDGAR](https://www.sec.gov/search-filings/edgar-application-programming-interfaces) | U.S. company filings and financial data | Public APIs do not require keys; the company-ticker endpoint returned 403 in this check. Not integrated. Filings are not live stock prices. |
| [European Central Bank data](https://data.ecb.europa.eu/help/api/overview) | Official statistics and reference exchange rates | One exchange-rate sample returned data; another timed out. Not integrated. Reference rates are not live trade prices. |
| [CNInfo](https://www.cninfo.com.cn/) | Chinese listed-company disclosures | Public starting point; API coverage and automated-use conditions require review. Not integrated. |
| [World Bank](https://datahelpdesk.worldbank.org/knowledgebase/articles/889392) | Macroeconomic, population, and social statistics | Annual country/indicator observations are integrated. |

Live stock quotes are not integrated. Stock sources require separate checks for exchange coverage, licensing, quote delay, currency, and timestamps. Historical data, reference prices, and live trades are not interchangeable.

## Health and other international organizations

[WHO Global Health Observatory](https://www.who.int/data/gho/info/gho-odata-api) provides health indicators. A sample against the older GHO endpoint returned 503; WHO has announced a migration, so the new API needs review before integration. Public feeds such as [UN News RSS](https://news.un.org/en/rss-feeds) could add organizational news and are not yet integrated. See the [full source research](https://github.com/wjason/xcoze-search/blob/main/research/free-sources-2026-11.en.md) for more organizations and datasets.

Checked on 2026-11-05 (Beijing time). A single response does not establish continuing availability, keyless access for every endpoint, or a commercial-use license.
