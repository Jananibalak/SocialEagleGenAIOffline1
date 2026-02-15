from typing import List, Dict, Any
from datetime import datetime
import json


class AnalysisEngine:
    """Generate personalized financial insights and recommendations"""
    
    def __init__(self):
        self.spending_thresholds = {
            'Groceries': 500,
            'Dining': 300,
            'Utilities': 200,
            'Entertainment': 200,
            'Transportation': 300,
            'Shopping': 400,
        }
    
    def generate_insights(self, bills_data: List[Dict], api_key: str) -> Dict[str, str]:
        """Generate comprehensive insights from bills"""
        total_spent = sum(bill.get('amount', 0) for bill in bills_data)
        category_totals = self._calculate_category_totals(bills_data)
        
        observations = self._generate_observations(bills_data, category_totals, total_spent)
        warnings = self._generate_warnings(category_totals)
        recommendations = self._generate_recommendations(bills_data, category_totals, total_spent)
        
        return {
            'observations': observations,
            'warnings': warnings,
            'recommendations': recommendations
        }
    
    def _calculate_category_totals(self, bills_data: List[Dict]) -> Dict[str, float]:
        """Calculate total spending per category"""
        totals = {}
        for bill in bills_data:
            category = bill.get('category', 'Other')
            amount = bill.get('amount', 0)
            totals[category] = totals.get(category, 0) + amount
        return totals
    
    def _generate_observations(self, bills_data: List[Dict], category_totals: Dict[str, float], total_spent: float) -> str:
        """Generate friendly observations about spending"""
        observations = []
        
        observations.append(f"📊 You've spent **${total_spent:,.2f}** across **{len(bills_data)} bills**. ")
        
        if category_totals:
            top_category = max(category_totals, key=category_totals.get)
            top_amount = category_totals[top_category]
            percentage = (top_amount / total_spent) * 100 if total_spent > 0 else 0
            
            observations.append(f"\n\n💰 Your biggest spending category is **{top_category}** at ${top_amount:,.2f} ({percentage:.1f}% of your total spending). ")
        
        merchants = [bill.get('merchant', 'Unknown') for bill in bills_data]
        if merchants:
            from collections import Counter
            merchant_counts = Counter(merchants)
            most_common = merchant_counts.most_common(1)[0]
            if most_common[1] > 1:
                observations.append(f"\n\n🏪 You've visited **{most_common[0]}** the most ({most_common[1]} times). Looks like you've found a favorite spot! ")
        
        return ''.join(observations)
    
    def _generate_warnings(self, category_totals: Dict[str, float]) -> str:
        """Generate warnings for overspending"""
        warnings = []
        
        for category, threshold in self.spending_thresholds.items():
            if category in category_totals and category_totals[category] > threshold:
                overspend = category_totals[category] - threshold
                warnings.append(f"• **{category}**: You're ${overspend:,.2f} over the recommended monthly budget of ${threshold:,.2f}. ")
        
        if not warnings:
            return "🎉 Great news! You're within reasonable spending limits across all categories. Keep it up!"
        
        warning_text = "I noticed you might be spending a bit more than usual in these areas:\n\n" + '\n'.join(warnings)
        warning_text += "\n\nDon't worry though - awareness is the first step to better budgeting! 💪"
        
        return warning_text
    
    def _generate_recommendations(self, bills_data: List[Dict], category_totals: Dict[str, float], total_spent: float) -> str:
        """Generate personalized recommendations"""
        recommendations = []
        
        if 'Dining' in category_totals and category_totals['Dining'] > 200:
            dining_percentage = (category_totals['Dining'] / total_spent) * 100
            recommendations.append(f"🍽️ **Dining Out**: You spent ${category_totals['Dining']:,.2f} ({dining_percentage:.1f}% of total). Consider meal prepping on Sundays - it's fun, healthy, and could save you $100-200/month!")
        
        groceries = category_totals.get('Groceries', 0)
        dining = category_totals.get('Dining', 0)
        if dining > groceries and dining > 0:
            recommendations.append(f"\n\n🥗 **Food Balance**: You're spending more on dining (${dining:,.2f}) than groceries (${groceries:,.2f}). Shifting even 30% of dining to home cooking could save you big! Try cooking 2-3 meals at home per week to start.")
        
        if 'Entertainment' in category_totals:
            recommendations.append(f"\n\n📺 **Subscription Check**: With ${category_totals['Entertainment']:,.2f} in entertainment, it might be time for a subscription audit. Are you using all those streaming services? Cutting just one could save $10-15/month!")
        
        if 'Shopping' in category_totals and category_totals['Shopping'] > 300:
            recommendations.append(f"\n\n🛍️ **Smart Shopping**: ${category_totals['Shopping']:,.2f} on shopping. Try the 24-hour rule: wait a day before buying non-essentials. You'd be surprised how many impulse purchases you'll skip!")
        
        potential_savings = total_spent * 0.15
        recommendations.append(f"\n\n💡 **Quick Win**: By making small changes in your top spending categories, you could potentially save around **${potential_savings:,.2f}** per month. That's ${potential_savings * 12:,.2f} a year! 🎯")
        
        if not recommendations:
            recommendations.append("✨ You're doing great! Your spending looks balanced. Keep tracking your bills to maintain this good habit! 🌟")
        
        return ''.join(recommendations)
