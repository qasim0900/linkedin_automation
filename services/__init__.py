"""
Services module for LinkedIn automation system.
Contains decision logic and rate limiting services.
"""

import logging
import random
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass

from config import config
from database import db_manager

logger = logging.getLogger(__name__)

@dataclass
class ProfileScore:
    """Profile scoring data structure."""
    profile_url: str
    score: float
    factors: Dict[str, float]
    priority: str

class ProfileSelector:
    """Intelligent profile selection for automation."""
    
    def __init__(self):
        self.scoring_weights = {
            "location_relevance": 0.3,
            "title_relevance": 0.25,
            "company_relevance": 0.2,
            "connection_potential": 0.15,
            "activity_level": 0.1
        }
    
    def select_profiles_for_connection(self, limit: int = 20, location: str = "USA") -> List[ProfileScore]:
        """Select best profiles for connection requests."""
        try:
            # Get unprocessed profiles
            profiles = list(db_manager.get_unprocessed_profiles(limit * 2))  # Get more to score
            
            scored_profiles = []
            
            for profile in profiles:
                score_data = self._calculate_profile_score(profile, location)
                if score_data.score > 0.5:  # Minimum threshold
                    scored_profiles.append(score_data)
            
            # Sort by score and return top profiles
            scored_profiles.sort(key=lambda x: x.score, reverse=True)
            
            # Assign priorities
            for i, profile in enumerate(scored_profiles[:limit]):
                if profile.score >= 0.8:
                    profile.priority = "high"
                elif profile.score >= 0.6:
                    profile.priority = "medium"
                else:
                    profile.priority = "low"
            
            logger.info(f"Selected {len(scored_profiles[:limit])} profiles for connection")
            return scored_profiles[:limit]
        
        except Exception as e:
            logger.error(f"Error selecting profiles for connection: {e}")
            return []
    
    def select_profiles_for_messaging(self, limit: int = 15) -> List[ProfileScore]:
        """Select profiles for messaging (already connected)."""
        try:
            query = {
                "connected": True,
                "$or": [
                    {"messaged": {"$exists": False}},
                    {"messaged": False}
                ]
            }
            
            profiles = list(db_manager.profiles_collection.find(query).limit(limit * 2))
            
            scored_profiles = []
            
            for profile in profiles:
                score_data = self._calculate_messaging_score(profile)
                if score_data.score > 0.4:  # Lower threshold for messaging
                    scored_profiles.append(score_data)
            
            scored_profiles.sort(key=lambda x: x.score, reverse=True)
            
            logger.info(f"Selected {len(scored_profiles[:limit])} profiles for messaging")
            return scored_profiles[:limit]
        
        except Exception as e:
            logger.error(f"Error selecting profiles for messaging: {e}")
            return []
    
    def _calculate_profile_score(self, profile: Dict[str, Any], target_location: str) -> ProfileScore:
        """Calculate score for a profile based on various factors."""
        factors = {}
        
        # Location relevance
        profile_location = profile.get("location", "").lower()
        if target_location.lower() in profile_location:
            factors["location_relevance"] = 1.0
        elif "united states" in profile_location or "usa" in profile_location:
            factors["location_relevance"] = 0.8
        else:
            factors["location_relevance"] = 0.3
        
        # Title relevance
        title = profile.get("title", "").lower()
        relevant_titles = ["software engineer", "developer", "programmer", "engineer", "technical"]
        factors["title_relevance"] = sum(0.2 for rt in relevant_titles if rt in title)
        factors["title_relevance"] = min(factors["title_relevance"], 1.0)
        
        # Company relevance
        company = profile.get("company", "").lower()
        tech_companies = ["google", "microsoft", "amazon", "apple", "facebook", "meta", "netflix"]
        factors["company_relevance"] = sum(0.3 for tc in tech_companies if tc in company)
        factors["company_relevance"] = min(factors["company_relevance"], 1.0)
        
        # Connection potential (based on profile completeness)
        factors["connection_potential"] = 0.7  # Default assumption
        
        # Activity level (based on recent activity if available)
        factors["activity_level"] = random.uniform(0.5, 1.0)  # Placeholder
        
        # Calculate weighted score
        total_score = sum(
            factors[factor] * self.scoring_weights[factor]
            for factor in self.scoring_weights
        )
        
        return ProfileScore(
            profile_url=profile.get("href", ""),
            score=total_score,
            factors=factors,
            priority=""
        )
    
    def _calculate_messaging_score(self, profile: Dict[str, Any]) -> ProfileScore:
        """Calculate score for messaging based on connection quality."""
        factors = {}
        
        # Time since connection (recent connections have higher priority)
        connection_date = profile.get("connection_date")
        if connection_date:
            days_since = (datetime.utcnow() - connection_date).days
            if days_since <= 7:
                factors["connection_recency"] = 1.0
            elif days_since <= 30:
                factors["connection_recency"] = 0.7
            else:
                factors["connection_recency"] = 0.4
        else:
            factors["connection_recency"] = 0.5
        
        # Profile engagement potential
        factors["engagement_potential"] = random.uniform(0.6, 1.0)
        
        # Message timing
        factors["timing_score"] = 0.8  # Default good timing
        
        # Calculate weighted score
        messaging_weights = {
            "connection_recency": 0.4,
            "engagement_potential": 0.4,
            "timing_score": 0.2
        }
        
        total_score = sum(
            factors[factor] * messaging_weights[factor]
            for factor in messaging_weights
        )
        
        return ProfileScore(
            profile_url=profile.get("href", ""),
            score=total_score,
            factors=factors,
            priority=""
        )

class RateLimitService:
    """Advanced rate limiting and scheduling service."""
    
    def __init__(self):
        self.daily_limits = {
            "connections": config.MAX_CONNECTIONS_PER_DAY,
            "messages": config.MAX_MESSAGES_PER_DAY,
            "visits": config.MAX_PROFILE_VISITS_PER_DAY
        }
        
        self.hourly_limits = {
            "connections": 5,  # Max 5 connections per hour
            "messages": 3,    # Max 3 messages per hour
            "visits": 10       # Max 10 visits per hour
        }
    
    def can_perform_action(self, action_type: str) -> Tuple[bool, str]:
        """Check if an action can be performed based on rate limits."""
        try:
            # Check daily limits
            daily_stats = db_manager.get_daily_stats()
            daily_count = daily_stats.get(action_type, 0)
            
            if daily_count >= self.daily_limits[action_type]:
                return False, f"Daily {action_type} limit reached ({daily_count}/{self.daily_limits[action_type]})"
            
            # Check hourly limits
            hourly_count = self._get_hourly_count(action_type)
            if hourly_count >= self.hourly_limits[action_type]:
                return False, f"Hourly {action_type} limit reached ({hourly_count}/{self.hourly_limits[action_type]})"
            
            # Check cooldown periods
            if not self._check_cooldown(action_type):
                return False, f"Cooldown period active for {action_type}"
            
            return True, "Action allowed"
        
        except Exception as e:
            logger.error(f"Error checking rate limits: {e}")
            return False, "Error checking limits"
    
    def _get_hourly_count(self, action_type: str) -> int:
        """Get count of actions in the last hour."""
        try:
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)
            
            pipeline = [
                {"$match": {
                    "action_type": action_type,
                    "timestamp": {"$gte": one_hour_ago}
                }},
                {"$count": "count"}
            ]
            
            result = list(db_manager.activity_log_collection.aggregate(pipeline))
            return result[0]["count"] if result else 0
        
        except Exception as e:
            logger.error(f"Error getting hourly count: {e}")
            return 0
    
    def _check_cooldown(self, action_type: str) -> bool:
        """Check if cooldown period has passed."""
        try:
            cooldown_periods = {
                "connections": 300,    # 5 minutes between connections
                "messages": 600,       # 10 minutes between messages
                "visits": 60           # 1 minute between visits
            }
            
            # Get last action timestamp
            last_action = db_manager.activity_log_collection.find_one(
                {"action_type": action_type},
                sort=[("timestamp", -1)]
            )
            
            if not last_action:
                return True
            
            time_since_last = (datetime.utcnow() - last_action["timestamp"]).total_seconds()
            cooldown_period = cooldown_periods.get(action_type, 60)
            
            return time_since_last >= cooldown_period
        
        except Exception as e:
            logger.error(f"Error checking cooldown: {e}")
            return True  # Allow action if error occurs
    
    def get_next_available_time(self, action_type: str) -> Optional[datetime]:
        """Get when the next action of this type can be performed."""
        try:
            # Check daily limit reset
            daily_stats = db_manager.get_daily_stats()
            if daily_stats.get(action_type, 0) >= self.daily_limits[action_type]:
                # Reset at midnight
                tomorrow = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
                tomorrow += timedelta(days=1)
                return tomorrow
            
            # Check hourly limit
            hourly_count = self._get_hourly_count(action_type)
            if hourly_count >= self.hourly_limits[action_type]:
                # Reset in next hour
                next_hour = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
                next_hour += timedelta(hours=1)
                return next_hour
            
            # Check cooldown
            last_action = db_manager.activity_log_collection.find_one(
                {"action_type": action_type},
                sort=[("timestamp", -1)]
            )
            
            if last_action:
                cooldown_periods = {
                    "connections": 300,
                    "messages": 600,
                    "visits": 60
                }
                
                cooldown_period = cooldown_periods.get(action_type, 60)
                next_available = last_action["timestamp"] + timedelta(seconds=cooldown_period)
                
                if next_available > datetime.utcnow():
                    return next_available
            
            return None
        
        except Exception as e:
            logger.error(f"Error getting next available time: {e}")
            return None
    
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """Get comprehensive rate limit status."""
        try:
            status = {}
            
            for action_type in self.daily_limits.keys():
                daily_stats = db_manager.get_daily_stats()
                daily_count = daily_stats.get(action_type, 0)
                hourly_count = self._get_hourly_count(action_type)
                
                can_perform, reason = self.can_perform_action(action_type)
                next_available = self.get_next_available_time(action_type)
                
                status[action_type] = {
                    "daily_used": daily_count,
                    "daily_limit": self.daily_limits[action_type],
                    "hourly_used": hourly_count,
                    "hourly_limit": self.hourly_limits[action_type],
                    "can_perform": can_perform,
                    "reason": reason,
                    "next_available": next_available.isoformat() if next_available else None
                }
            
            return status
        
        except Exception as e:
            logger.error(f"Error getting rate limit status: {e}")
            return {}

class DecisionEngine:
    """Main decision engine for automation actions."""
    
    def __init__(self):
        self.profile_selector = ProfileSelector()
        self.rate_limiter = RateLimitService()
    
    def get_next_action(self) -> Optional[Dict[str, Any]]:
        """Decide the next action to perform."""
        try:
            # Check rate limits for each action type
            actions = ["connections", "messages", "visits"]
            available_actions = []
            
            for action in actions:
                can_perform, reason = self.rate_limiter.can_perform_action(action)
                if can_perform:
                    available_actions.append(action)
            
            if not available_actions:
                return None
            
            # Prioritize actions based on strategy
            action_priorities = {
                "connections": 3,  # High priority
                "visits": 2,        # Medium priority  
                "messages": 1       # Lower priority (after connections)
            }
            
            # Sort by priority
            available_actions.sort(key=lambda x: action_priorities[x], reverse=True)
            next_action = available_actions[0]
            
            # Get profiles for this action
            if next_action == "connections":
                profiles = self.profile_selector.select_profiles_for_connection()
            elif next_action == "messages":
                profiles = self.profile_selector.select_profiles_for_messaging()
            else:  # visits
                profiles = list(db_manager.get_unprocessed_profiles(20))
            
            if not profiles:
                return None
            
            return {
                "action_type": next_action,
                "profiles": profiles[:10],  # Limit to 10 profiles
                "estimated_time": self._estimate_action_time(next_action, len(profiles))
            }
        
        except Exception as e:
            logger.error(f"Error getting next action: {e}")
            return None
    
    def _estimate_action_time(self, action_type: str, profile_count: int) -> int:
        """Estimate time required for action in minutes."""
        time_per_action = {
            "connections": 8,   # 8 minutes per connection
            "messages": 12,    # 12 minutes per message
            "visits": 3        # 3 minutes per visit
        }
        
        return profile_count * time_per_action.get(action_type, 5)
    
    def should_take_break(self) -> bool:
        """Decide if it's time to take a break."""
        try:
            # Check recent activity
            recent_actions = db_manager.activity_log_collection.count_documents({
                "timestamp": {"$gte": datetime.utcnow() - timedelta(minutes=30)}
            })
            
            # Take break after 15 actions in 30 minutes
            if recent_actions >= 15:
                return True
            
            # Random break chance
            return random.random() < 0.1  # 10% chance
        
        except Exception as e:
            logger.error(f"Error checking break requirement: {e}")
            return False

# Global service instances
profile_selector = ProfileSelector()
rate_limit_service = RateLimitService()
decision_engine = DecisionEngine()