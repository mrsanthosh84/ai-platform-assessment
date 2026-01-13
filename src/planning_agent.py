#!/usr/bin/env python3
import os
import json
import requests
from typing import Dict, List, Any
from dotenv import load_dotenv

# Suppress OpenAI pydantic warning
import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore", UserWarning)
    from openai import OpenAI

load_dotenv()

class PlanningAgent:
    def __init__(self):
        try:
            self.client = OpenAI(
                base_url=os.getenv("OPENAI_BASE_URL"),
                api_key=os.getenv("OPENAI_API_KEY")
            )
            self.is_mock = False
            print("✅ Using real OpenAI API")
        except Exception as e:
            # Mock OpenAI for Python 3.14 compatibility
            class MockOpenAI:
                def __init__(self, **kwargs):
                    pass
                class Chat:
                    class Completions:
                        def create(self, **kwargs):
                            class MockResponse:
                                def __init__(self):
                                    self.choices = [type('obj', (object,), {
                                        'message': type('obj', (object,), {
                                            'content': '{"destination": "Auckland", "duration": 2, "budget_amount": 500, "budget_currency": "NZD", "preferences": []}'
                                        })()
                                    })()]
                            return MockResponse()
                    @property
                    def completions(self):
                        return self.Completions()
                @property
                def chat(self):
                    return self.Chat()
            
            self.client = MockOpenAI()
            self.is_mock = True
            print("⚠️  Using mock planning (OpenAI library incompatible with Python 3.14)")
        
        self.model = os.getenv("MODEL_NAME", "gpt-4")
        self.scratchpad = []
        
    def log_reasoning(self, thought: str):
        self.scratchpad.append(f"[REASONING] {thought}")
        print(f"{thought}")
    
    def get_flight_prices(self, origin: str, destination: str, date: str) -> Dict:
        """Mock flight API - in real implementation would call actual API"""
        self.log_reasoning(f"Checking flights from {origin} to {destination} on {date}")
        
        # Mock data with lower prices to stay within budget
        flights = [
            {"airline": "Air New Zealand", "price": 120, "departure": "08:00", "arrival": "10:30"},
            {"airline": "Jetstar", "price": 100, "departure": "14:00", "arrival": "16:30"},
            {"airline": "Virgin Australia", "price": 110, "departure": "18:00", "arrival": "20:30"}
        ]
        
        return {"flights": flights, "currency": "NZD"}
    
    def get_weather(self, city: str, date: str) -> Dict:
        """Mock weather API"""
        self.log_reasoning(f"Checking weather for {city} on {date}")
        
        # Mock weather data
        weather = {
            "temperature": "18°C",
            "condition": "Partly cloudy",
            "precipitation": "20%",
            "recommendation": "Light jacket recommended"
        }
        
        return weather
    
    def get_attractions(self, city: str) -> Dict:
        """Mock attractions API"""
        self.log_reasoning(f"Finding attractions in {city}")
        
        attractions = [
            {"name": "Sky Tower", "price": 25, "duration": "2 hours", "category": "landmark"},
            {"name": "Auckland Museum", "price": 20, "duration": "3 hours", "category": "museum"},
            {"name": "Waiheke Island", "price": 35, "duration": "full day", "category": "nature"},
            {"name": "Harbour Bridge Climb", "price": 80, "duration": "3 hours", "category": "adventure"},
            {"name": "Kelly Tarlton's", "price": 30, "duration": "2 hours", "category": "aquarium"}
        ]
        
        return {"attractions": attractions}
    
    def get_accommodation(self, city: str, budget_per_night: float) -> Dict:
        """Mock accommodation API"""
        self.log_reasoning(f"Finding accommodation in {city} under ${budget_per_night}/night")
        
        accommodations = [
            {"name": "Auckland City Hotel", "price": 80, "rating": 4.2, "type": "hotel"},
            {"name": "Backpackers Central", "price": 30, "rating": 3.8, "type": "hostel"},
            {"name": "Airbnb Downtown", "price": 60, "rating": 4.5, "type": "apartment"},
            {"name": "YHA Auckland", "price": 40, "rating": 4.0, "type": "hostel"}
        ]
        
        suitable = [acc for acc in accommodations if acc["price"] <= budget_per_night]
        return {"accommodations": suitable}
    
    def plan_trip(self, prompt: str) -> Dict:
        """Main planning function"""
        self.scratchpad = []
        self.log_reasoning("Starting trip planning process")
        
        # Parse the prompt using LLM
        parse_prompt = f"""
        Extract the following information from this trip request:
        - Destination city
        - Duration (number of days)
        - Budget (total amount and currency)
        - Any specific preferences or constraints
        
        Request: "{prompt}"
        
        Return as JSON with keys: destination, duration, budget_amount, budget_currency, preferences
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": parse_prompt}],
                max_tokens=200
            )
            
            trip_params = json.loads(response.choices[0].message.content)
            
        except Exception as e:
            # Fallback parsing
            if self.is_mock:
                print(f"Using mock trip parameters (OpenAI not available)")
            
            trip_params = {
                "destination": "Auckland",
                "duration": 2,
                "budget_amount": 500,
                "budget_currency": "NZD",
                "preferences": []
            }
        
        self.log_reasoning(f"Parsed parameters: {trip_params}")
        
        # Calculate budget allocation
        total_budget = trip_params["budget_amount"]
        duration = trip_params["duration"]
        
        # Budget allocation: 40% accommodation, 30% activities, 20% food, 10% transport
        accommodation_budget = total_budget * 0.4
        activities_budget = total_budget * 0.3
        food_budget = total_budget * 0.2
        transport_budget = total_budget * 0.1
        
        per_night_budget = accommodation_budget / duration
        
        self.log_reasoning(f"Budget allocation - Accommodation: ${accommodation_budget:.0f}, Activities: ${activities_budget:.0f}")
        
        # Call tools
        weather = self.get_weather(trip_params["destination"], "2024-01-15")
        attractions = self.get_attractions(trip_params["destination"])
        accommodation = self.get_accommodation(trip_params["destination"], per_night_budget)
        flights = self.get_flight_prices("Wellington", trip_params["destination"], "2024-01-15")
        
        # Select best options within budget
        selected_accommodation = min(accommodation["accommodations"], key=lambda x: x["price"])
        
        # Select attractions within budget
        selected_attractions = []
        remaining_activities_budget = activities_budget
        
        for attraction in sorted(attractions["attractions"], key=lambda x: x["price"]):
            if attraction["price"] <= remaining_activities_budget:
                selected_attractions.append(attraction)
                remaining_activities_budget -= attraction["price"]
                if len(selected_attractions) >= duration:  # One main activity per day
                    break
        
        # Select cheapest flight
        selected_flight = min(flights["flights"], key=lambda x: x["price"])
        
        # Calculate total cost
        total_cost = (selected_accommodation["price"] * duration + 
                     sum(a["price"] for a in selected_attractions) + 
                     selected_flight["price"] * 2 +  # Return flight
                     food_budget)
        
        self.log_reasoning(f"Total estimated cost: ${total_cost:.0f}")
        
        # Generate itinerary
        itinerary = {
            "destination": trip_params["destination"],
            "duration": f"{duration} days",
            "total_budget": total_budget,
            "estimated_cost": round(total_cost, 2),
            "budget_remaining": round(total_budget - total_cost, 2),
            "accommodation": {
                "name": selected_accommodation["name"],
                "type": selected_accommodation["type"],
                "price_per_night": selected_accommodation["price"],
                "total_cost": selected_accommodation["price"] * duration
            },
            "flights": {
                "outbound": selected_flight,
                "return": selected_flight,
                "total_cost": selected_flight["price"] * 2
            },
            "activities": selected_attractions,
            "daily_schedule": [],
            "weather_forecast": weather,
            "reasoning_log": self.scratchpad
        }
        
        # Create daily schedule
        for day in range(1, duration + 1):
            day_plan = {
                "day": day,
                "activities": selected_attractions[day-1:day] if day-1 < len(selected_attractions) else [],
                "meals": f"Budget: ${food_budget/duration:.0f}",
                "notes": weather["recommendation"] if day == 1 else "Enjoy your day!"
            }
            itinerary["daily_schedule"].append(day_plan)
        
        return itinerary

def main():
    print("🤖 Autonomous Planning Agent")
    print("=" * 40)
    
    try:
        agent = PlanningAgent()
        
        print("Example: 'Plan a 2-day trip to Auckland for under NZ$500'")
        
        while True:
            prompt = input("\nEnter your trip request (or 'quit'): ")
            if prompt.lower() == 'quit':
                break
            
            print("\n" + "="*50)
            try:
                itinerary = agent.plan_trip(prompt)
                
                print("\nFINAL ITINERARY")
                print("="*50)
                print(json.dumps(itinerary, indent=2))
                
            except Exception as e:
                print(f"Error planning trip: {e}")
                print("The planning agent encountered an error. Try a simpler request.")
                
    except Exception as e:
        print(f"Error initializing planning agent: {e}")
        print("Try using Docker for full functionality: docker-compose up --build")

if __name__ == "__main__":
    main()