
import requests

API_URL = "https://api.frankfurter.dev/v2/rate"


def get_exchange_rate(from_currency: str, to_currency: str) -> dict:
    """
    Get the latest available exchange rate between two currencies.

    Args:
        from_currency: The source currency code (e.g. USD).
        to_currency: The target currency code (e.g. BDT).

    Returns:
        Dictionary containing the exchange rate information.
    """

    print("Currency Exchange tool called")

    # Normalize currency codes
    from_currency = from_currency.strip().upper()
    to_currency = to_currency.strip().upper()

    # Basic input validation
    if not from_currency or not to_currency:
        return {"error": "Both currency codes are required."}

    if len(from_currency) != 3 or len(to_currency) != 3:
        return {"error": "Currency codes must be 3 characters (e.g. USD, BDT)."}

    # Avoid unnecessary API calls
    if from_currency == to_currency:
        return {
            "base": from_currency,
            "quote": to_currency,
            "rate": 1.0,
            "message": "Both currencies are the same."
        }

    url = f"{API_URL}/{from_currency}/{to_currency}"

    try:
        response = requests.get(url, timeout=10)

        response.raise_for_status()

        data = response.json()

        return {
            "date": data["date"],
            "from_currency": data["base"],
            "to_currency": data["quote"],
            "exchange_rate": data["rate"]
        }

    except requests.exceptions.HTTPError:
        try:
            error_data = response.json()
            return {
                "error": error_data.get(
                    "message",
                    "Invalid currency or exchange rate unavailable."
                )
            }
        except ValueError:
            return {"error": "Currency API returned an HTTP error."}

    except requests.exceptions.Timeout:
        return {"error": "Currency API request timed out."}

    except requests.exceptions.RequestException as e:
        return {"error": f"Network error: {str(e)}"}

    except (KeyError, TypeError):
        return {"error": "Unexpected response format from currency API."}
