from ml.forecast_generator import generate_forecast


def generate_ml_recommendations(
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

        change_percent = row[
            "Demand_Change_Percent"
        ]

        predicted_demand = row[
            "Predicted_Next_Week"
        ]

        current_demand = row[
            "Current_Weekly_Demand"
        ]

        if change_percent >= 5:

            recommendations.append({

                "area":
                    "Inventory",

                "priority":
                    "High",

                "recommendation":
                    (
                        f"{product} is forecast to increase "
                        f"by {change_percent:.2f}% next week. "
                        f"Consider increasing inventory to "
                        f"approximately "
                        f"{predicted_demand:.0f} units."
                    )

            })

            recommendations.append({

                "area":
                    "Product Opportunity",

                "priority":
                    "High",

                "recommendation":
                    (
                        f"{product} shows strong expected "
                        f"demand growth. Consider prioritizing "
                        f"stock availability and monitoring "
                        f"sales closely."
                    )

            })

        elif change_percent > 0:

            recommendations.append({

                "area":
                    "Inventory",

                "priority":
                    "Medium",

                "recommendation":
                    (
                        f"{product} is forecast to increase "
                        f"by {change_percent:.2f}% next week. "
                        f"Consider maintaining slightly "
                        f"higher inventory levels."
                    )

            })

        elif change_percent <= -5:

            recommendations.append({

                "area":
                    "Inventory",

                "priority":
                    "Medium",

                "recommendation":
                    (
                        f"{product} is forecast to decrease "
                        f"by {abs(change_percent):.2f}% next week. "
                        f"Consider avoiding excess inventory "
                        f"and reviewing stock levels."
                    )

            })

            recommendations.append({

                "area":
                    "Demand Monitoring",

                "priority":
                    "Medium",

                "recommendation":
                    (
                        f"{product} demand is showing a "
                        f"significant expected decline. "
                        f"Monitor sales closely and investigate "
                        f"possible causes."
                    )

            })

        else:

            recommendations.append({

                "area":
                    "Demand Monitoring",

                "priority":
                    "Low",

                "recommendation":
                    (
                        f"{product} demand is expected to remain "
                        f"relatively stable next week. "
                        f"Continue monitoring demand patterns."
                    )

            })

    return recommendations

if __name__ == "__main__":

    print(
        "===== SBI-ADS ML DECISION SUPPORT ====="
    )

    recommendations = (
        generate_ml_recommendations()
    )

    for index, item in enumerate(
        recommendations,
        start=1
    ):

        print(
            f"\n{index}. "
            f"Area: {item['area']}"
        )

        print(
            f"   Priority: "
            f"{item['priority']}"
        )

        print(
            f"   Recommendation: "
            f"{item['recommendation']}"
        )
