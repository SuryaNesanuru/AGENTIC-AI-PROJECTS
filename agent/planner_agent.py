"""
AI Study Planner Agent

Uses LLM-based reasoning to generate intelligent study schedules.
Integrates with Hugging Face Inference API (free tier) for planning.
"""

import json
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta
import os
from dotenv import load_dotenv

load_dotenv()


class StudyPlannerAgent:
    """
    AI Agent that generates study plans using LLM reasoning.
    
    Features:
    - Analyzes subjects, priorities, and available time
    - Generates optimized daily schedules
    - Adapts to changes in user preferences
    - Provides motivational messages
    """
    
    # Hugging Face API configuration
    HF_API_URL = os.getenv("HF_API_URL", "https://api-inference.huggingface.co/models/google/flan-t5-large")
    HF_API_KEY = os.getenv("HF_API_KEY", "")
    
    # Motivational quotes database
    MOTIVATIONAL_QUOTES = [
        "The expert in anything was once a beginner.",
        "Success is the sum of small efforts repeated day in and day out.",
        "Believe you can and you're halfway there.",
        "The future belongs to those who believe in the beauty of their dreams.",
        "Don't watch the clock; do what it does. Keep going.",
        "You are capable of amazing things.",
        "The only way to do great work is to love what you do.",
        "Keep your face always toward the sunshine—and shadows will fall behind you.",
        "Your limitation—it's only your imagination.",
        "Great things never came from comfort zones."
    ]
    
    def __init__(self, use_llm: bool = True):
        """
        Initialize the study planner agent.
        
        Args:
            use_llm: Whether to use LLM API (falls back to rule-based if False)
        """
        self.use_llm = use_llm and bool(self.HF_API_KEY)
        self.planning_history = []
    
    def generate_study_plan(
        self,
        subjects: List[Dict[str, Any]],
        exam_date: date,
        daily_hours: float,
        start_date: date = None
    ) -> List[Dict[str, Any]]:
        """
        Generate a complete study plan.
        
        Args:
            subjects: List of subject dicts with name, priority, difficulty, hours
            exam_date: Target exam date
            daily_hours: Available study hours per day
            start_date: Plan start date (defaults to today)
            
        Returns:
            List of daily study plan entries
        """
        start_date = start_date or date.today()
        days_available = (exam_date - start_date).days
        
        if days_available <= 0:
            raise ValueError("Exam date must be in the future!")
        
        # Calculate total hours needed
        total_hours_needed = sum(subj.get('hours_allocated', 2) for subj in subjects)
        total_hours_available = daily_hours * days_available
        
        # Adjust allocation based on availability
        if total_hours_needed > total_hours_available:
            # Scale down proportionally
            scale_factor = total_hours_available / max(total_hours_needed, 1)
            for subj in subjects:
                subj['adjusted_hours'] = subj.get('hours_allocated', 2) * scale_factor
        else:
            for subj in subjects:
                subj['adjusted_hours'] = subj.get('hours_allocated', 2)
        
        # Use LLM if available, otherwise use rule-based planning
        if self.use_llm:
            plan = self._generate_with_llm(subjects, exam_date, daily_hours, start_date)
        else:
            plan = self._generate_rule_based(subjects, exam_date, daily_hours, start_date)
        
        self.planning_history.append({
            'timestamp': datetime.now(),
            'subjects_count': len(subjects),
            'days_planned': days_available,
            'plan_entries': len(plan)
        })
        
        return plan
    
    def _generate_with_llm(
        self,
        subjects: List[Dict[str, Any]],
        exam_date: date,
        daily_hours: float,
        start_date: date
    ) -> List[Dict[str, Any]]:
        """Generate study plan using LLM reasoning."""
        
        # Prepare prompt for LLM
        prompt = self._create_planning_prompt(subjects, exam_date, daily_hours, start_date)
        
        try:
            # Call Hugging Face API
            response = self._query_huggingface_api(prompt)
            
            # Parse LLM response
            if response:
                plan = self._parse_llm_response(response, subjects, start_date)
                if plan:
                    return plan
        except Exception as e:
            print(f"LLM API failed, falling back to rule-based: {e}")
        
        # Fallback to rule-based
        return self._generate_rule_based(subjects, exam_date, daily_hours, start_date)
    
    def _create_planning_prompt(
        self,
        subjects: List[Dict[str, Any]],
        exam_date: date,
        daily_hours: float,
        start_date: date
    ) -> str:
        """Create a detailed prompt for the LLM."""
        
        days = (exam_date - start_date).days
        
        subject_info = "\n".join([
            f"- {s['name']}: Priority {s.get('priority', 2)}, Difficulty {s.get('difficulty', 3)}, "
            f"Needs {s.get('adjusted_hours', s.get('hours_allocated', 2))} hours"
            for s in subjects
        ])
        
        prompt = f"""
You are an expert study planner. Create a detailed daily study schedule.

CONTEXT:
- Exam Date: {exam_date.strftime('%Y-%m-%d')} ({days} days from start)
- Daily Study Hours: {daily_hours} hours
- Start Date: {start_date.strftime('%Y-%m-%d')}

SUBJECTS TO COVER:
{subject_info}

INSTRUCTIONS:
1. Distribute subjects across available days
2. Prioritize high-priority subjects early
3. Allocate more time for difficult subjects
4. Include revision time before exam
5. Balance subjects to avoid burnout

OUTPUT FORMAT (JSON array):
[
  {{
    "date": "YYYY-MM-DD",
    "time_slot": "HH:MM-HH:MM",
    "subject": "Subject Name",
    "duration_hours": 2.0,
    "topic": "Specific topic to cover"
  }},
  ...
]

Generate the complete study plan as JSON:
"""
        return prompt
    
    def _query_huggingface_api(self, prompt: str) -> Optional[str]:
        """Query Hugging Face Inference API."""
        
        if not self.HF_API_KEY:
            return None
        
        headers = {
            "Authorization": f"Bearer {self.HF_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 1024,
                "temperature": 0.7,
                "do_sample": True,
                "top_p": 0.95
            }
        }
        
        try:
            response = requests.post(
                self.HF_API_URL,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get('generated_text', '')
                elif isinstance(result, dict):
                    return result.get('generated_text', '')
        except requests.exceptions.RequestException:
            pass
        
        return None
    
    def _parse_llm_response(
        self,
        response: str,
        subjects: List[Dict[str, Any]],
        start_date: date
    ) -> Optional[List[Dict[str, Any]]]:
        """Parse LLM response into structured plan."""
        
        # Extract JSON from response
        import re
        json_match = re.search(r'\[[\s\S]*\]', response)
        
        if not json_match:
            return None
        
        try:
            plan_data = json.loads(json_match.group())
            
            # Create subject lookup
            subject_map = {s['name']: s for s in subjects}
            
            # Convert to standard format
            formatted_plan = []
            for entry in plan_data:
                subject_name = entry.get('subject', '')
                if subject_name not in subject_map:
                    continue
                
                date_str = entry.get('date', start_date.isoformat())
                try:
                    scheduled_date = datetime.fromisoformat(date_str).date()
                except ValueError:
                    scheduled_date = start_date
                
                formatted_plan.append({
                    'scheduled_date': scheduled_date,
                    'time_slot': entry.get('time_slot', '09:00-11:00'),
                    'subject_id': subject_map[subject_name]['id'],
                    'duration_hours': float(entry.get('duration_hours', 2)),
                    'topic': entry.get('topic', f"Study {subject_name}")
                })
            
            return formatted_plan if formatted_plan else None
            
        except json.JSONDecodeError:
            return None
    
    def _generate_rule_based(
        self,
        subjects: List[Dict[str, Any]],
        exam_date: date,
        daily_hours: float,
        start_date: date
    ) -> List[Dict[str, Any]]:
        """Generate study plan using rule-based algorithm."""
        
        days_available = (exam_date - start_date).days
        plan = []
        
        # Sort subjects by priority (high first) and difficulty
        sorted_subjects = sorted(
            subjects,
            key=lambda x: (x.get('priority', 2), x.get('difficulty', 3))
        )
        
        current_date = start_date
        subject_index = 0
        remaining_hours = {s['name']: s.get('adjusted_hours', s.get('hours_allocated', 2)) for s in subjects}
        
        while current_date < exam_date and any(h > 0 for h in remaining_hours.values()):
            # Allocate hours for this day
            hours_allocated_today = 0
            
            # Round-robin through subjects
            attempts = 0
            while hours_allocated_today < daily_hours and attempts < len(sorted_subjects):
                subject = sorted_subjects[subject_index % len(sorted_subjects)]
                subject_name = subject['name']
                
                if remaining_hours[subject_name] > 0:
                    # Allocate 1-2 hour blocks
                    block_size = min(2.0, daily_hours - hours_allocated_today, remaining_hours[subject_name])
                    
                    if block_size >= 0.5:  # Minimum 30 minutes
                        # Generate time slot
                        start_hour = 9 + int(hours_allocated_today)
                        end_hour = start_hour + int(block_size)
                        time_slot = f"{start_hour:02d}:00-{end_hour:02d}:00"
                        
                        plan.append({
                            'scheduled_date': current_date,
                            'time_slot': time_slot,
                            'subject_id': subject['id'],
                            'duration_hours': block_size,
                            'topic': f"Study {subject_name}"
                        })
                        
                        hours_allocated_today += block_size
                        remaining_hours[subject_name] -= block_size
                
                subject_index += 1
                attempts += 1
            
            current_date += timedelta(days=1)
        
        # Add revision days before exam
        revision_days = min(2, days_available)
        for i in range(revision_days):
            rev_date = exam_date - timedelta(days=i+1)
            for subject in sorted_subjects[:3]:  # Top 3 subjects
                plan.append({
                    'scheduled_date': rev_date,
                    'time_slot': '10:00-12:00',
                    'subject_id': subject['id'],
                    'duration_hours': 2.0,
                    'topic': f"Revision: {subject['name']}"
                })
        
        return plan
    
    def replan(
        self,
        existing_plan: List[Dict[str, Any]],
        changes: Dict[str, Any],
        current_date: date = None
    ) -> List[Dict[str, Any]]:
        """
        Replan based on user changes.
        
        Args:
            existing_plan: Current study plan
            changes: Dictionary of changes (new hours, removed subjects, etc.)
            current_date: Current date for rescheduling
            
        Returns:
            Updated study plan
        """
        # Filter out completed and past plans
        current_date = current_date or date.today()
        remaining_plan = [
            p for p in existing_plan
            if p['scheduled_date'] >= current_date and not p.get('completed', False)
        ]
        
        # Apply changes
        if 'hours_change' in changes:
            # Adjust durations based on percentage change
            multiplier = changes['hours_change']
            for plan_entry in remaining_plan:
                plan_entry['duration_hours'] *= multiplier
        
        if 'new_subject' in changes:
            # Add new subject to remaining days
            new_subj = changes['new_subject']
            # Add at least one session per week
            weeks_remaining = len(set(p['scheduled_date'] for p in remaining_plan)) // 7
            for week in range(weeks_remaining):
                remaining_plan.append({
                    'scheduled_date': current_date + timedelta(days=week*7),
                    'time_slot': '16:00-18:00',
                    'subject_id': new_subj['id'],
                    'duration_hours': 2.0,
                    'topic': f"Study {new_subj['name']}"
                })
        
        return remaining_plan
    
    def get_motivational_message(self) -> str:
        """Get a random motivational quote."""
        import random
        return random.choice(self.MOTIVATIONAL_QUOTES)
    
    def analyze_progress(self, completed: int, total: int) -> str:
        """
        Analyze progress and provide feedback.
        
        Args:
            completed: Number of completed sessions
            total: Total planned sessions
            
        Returns:
            Feedback message
        """
        if total == 0:
            return "No study sessions planned yet. Let's create a plan!"
        
        percentage = (completed / total) * 100
        
        if percentage >= 80:
            return f"🌟 Excellent! You've completed {percentage:.0f}% of your plan. Keep up the great work!"
        elif percentage >= 50:
            return f"👍 Good progress! You're {percentage:.0f}% done. Stay consistent!"
        elif percentage >= 25:
            return f"💪 You're getting started ({percentage:.0f}% complete). Push forward!"
        else:
            return f"📚 Time to begin! Only {percentage:.0f}% complete. Start with small steps."
