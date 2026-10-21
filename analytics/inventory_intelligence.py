from ml.forecast_generator import generate_forecast

SAFETY_BUFFER = 0.10


def generate_inventory_recommendations(
    file_path=None,
    column_mapping=None
):

    forecast = generate_forecast(
        file_path=file_path,
        column_mapping=column_mapping
    )

    recommendations = []

    for _, row in forecast.iterrows():

        product = row["Product"]

        current_demand = float(
            row["Current_Weekly_Demand"]
        )

        predicted_demand = float(
            row["Predicted_Next_Week"]
        )

        change_percent = float(
            row["Demand_Change_Percent"]
        )

        recommended_stock = round(
            predicted_demand *
            (1 + SAFETY_BUFFER)
        )

        if change_percent >= 5:

            action = "Increase Stock"

            priority = "High"

            explanation = (
                f"{product} is expected to experience "
                f"strong demand growth of "
                f"{change_percent:.2f}%. "
                f"Recommended stock is approximately "
                f"{recommended_stock} units."
            )

        elif change_percent > 0:

            action = "Slightly Increase"

            priority = "Medium"

            explanation = (
                f"{product} is expected to increase "
                f"by {change_percent:.2f}%. "
                f"Maintain slightly higher stock levels "
                f"with approximately "
                f"{recommended_stock} units recommended."
            )

        elif change_percent <= -5:

            action = "Reduce Stock"

            priority = "Medium"

            explanation = (
                f"{product} is expected to decrease "
                f"by {abs(change_percent):.2f}%. "
                f"Avoid excess inventory and consider "
                f"reducing stock levels."
            )

        else:

            action = "Maintain Stock"

            priority = "Low"

            explanation = (
                f"{product} demand is relatively stable. "
                f"Maintain approximately "
                f"{recommended_stock} units to provide "
                f"a 10% safety buffer."
            )

        recommendations.append({

            "product":
                product,

            "current_demand":
                round(current_demand, 2),

            "predicted_demand":
                round(predicted_demand, 2),

            "demand_change_percent":
                round(change_percent, 2),

            "recommended_stock":
                recommended_stock,

            "action":
                action,

            "priority":
                priority,

            "explanation":
                explanation

        })

    return recommendations

if __name__ == "__main__":

    print(
        "===== SBI-ADS INVENTORY INTELLIGENCE ====="
    )

    recommendations = (
        generate_inventory_recommendations()
    )

    for index, item in enumerate(
        recommendations,
        start=1
    ):

        print(
            f"\n{index}. {item['product']}"
        )

        print(
            f"   Current Demand: "
            f"{item['current_demand']}"
        )

        print(
            f"   Predicted Demand: "
            f"{item['predicted_demand']}"
        )

        print(
            f"   Recommended Stock: "
            f"{item['recommended_stock']}"
        )

        print(
            f"   Action: "
            f"{item['action']}"
        )

        print(
            f"   Priority: "
            f"{item['priority']}"
        )

        print(
            f"   Explanation: "
            f"{item['explanation']}"
        )
