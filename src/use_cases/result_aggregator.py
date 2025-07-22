# src/use_cases/result_aggregator.py
import logging
from typing import Dict, Any, Callable

logger = logging.getLogger(__name__)

class ResultAggregator:
    """
    Takes the raw outputs from all completed subtasks and synthesizes them
    into a single, coherent result summary.

    This version is designed to be generic and extensible. It uses a mapping to
    find a custom summary function for a given task type, but falls back to a
    smart, general-purpose summary if no custom one is found.
    """
    def __init__(self):
        # This map connects a task name from the TaskTree to a specific
        # function that knows how to build its summary.
        # It's easy to add new custom summaries here.
        self._aggregator_map: Dict[str, Callable] = {
            "Order Food": self._aggregate_food_order,
            "Trip Planning": self._aggregate_trip_plan,
            # Add other custom aggregators here, e.g.:
            # "Send Email": self._aggregate_send_email,
        }

    # --- Custom Summary Builders ---

    def _aggregate_food_order(self, results_cache: Dict[str, Any]) -> Dict[str, Any]:
        """Custom summary for the 'Order Food' task."""
        logger.info("Using custom aggregator for 'Order Food'")
        try:
            place_order_result = results_cache.get("Place Order", {})
            order_id = place_order_result.get("order_id", "N/A")
            message = place_order_result.get("confirmation_message", "Your order has been placed.")
            
            return {
                "title": "🍕 Your Food Order is Complete!",
                "message": message,
                "details": {
                    "Order ID": order_id,
                },
                "shareable_text": f"Just ordered dinner with Allin1! My order ID is {order_id}. #Food #AI"
            }
        except Exception as e:
            logger.error(f"Error in custom food aggregator: {e}")
            # If the custom aggregator fails, fall back to the generic one
            return self._aggregate_generic("Order Food", results_cache)

    def _aggregate_trip_plan(self, results_cache: Dict[str, Any]) -> Dict[str, Any]:
        """Custom summary for the 'Trip Planning' task."""
        logger.info("Using custom aggregator for 'Trip Planning'")
        # This is an example; you would flesh this out with real keys from your tools
        try:
            flight_result = results_cache.get("Search Flights", {})
            hotel_result = results_cache.get("Book hotel", {})
            
            return {
                "title": "✈️ Your Trip Itinerary is Ready!",
                "message": "We've successfully planned your trip.",
                "details": {
                    "Flight Info": flight_result.get("details", "Not booked"),
                    "Hotel Info": hotel_result.get("hotel_name", "Not booked"),
                },
                "shareable_text": "My next trip is planned thanks to Allin1! #Travel #Automation"
            }
        except Exception as e:
            logger.error(f"Error in custom trip aggregator: {e}")
            return self._aggregate_generic("Trip Planning", results_cache)

    # --- The Smart, Generic Fallback ---

    def _aggregate_generic(self, task_type: str, results_cache: Dict[str, Any]) -> Dict[str, Any]:
        """
        A smart, general-purpose aggregator that works for ANY task.
        It creates a structured summary from the final subtask's result.
        """
        logger.warning(f"Using generic aggregator for task type: '{task_type}'.")
        
        # Get the name and result of the very last subtask
        final_subtask_name = list(results_cache.keys())[-1]
        final_result = results_cache.get(final_subtask_name, {})

        # Default title and message
        title = f"✅ Task '{task_type}' Completed"
        message = "All steps were executed successfully."
        
        # If the final result is a dictionary, use its contents for the message and details
        if isinstance(final_result, dict):
            # Try to find a meaningful message from common keys
            message_keys = ["message", "confirmation_message", "status_message", "details"]
            for key in message_keys:
                if key in final_result:
                    message = final_result[key]
                    break
            details = final_result
        else:
            # If the result is just a string or other type, display it simply
            details = {"final_output": str(final_result)}
            
        return {
            "title": title,
            "message": message,
            "details": details,
            "shareable_text": f"I just completed a '{task_type}' task using Allin1! #Productivity #AI"
        }

    # --- Main Public Method ---

    async def aggregate(self, task_type: str, results_cache: Dict[str, Any]) -> Dict[str, Any]:
        """

        Main aggregation method. It looks up a custom aggregator in the map and,
        if not found, delegates to the generic fallback aggregator.
        """
        logger.info(f"Aggregating results for task type: '{task_type}'")
        
        # Find the appropriate summary builder function for the task
        aggregator_function = self._aggregator_map.get(task_type)
        
        if aggregator_function:
            # If a custom aggregator is found, use it.
            return aggregator_function(results_cache)
        else:
            # Otherwise, use the smart generic fallback.
            return self._aggregate_generic(task_type, results_cache)