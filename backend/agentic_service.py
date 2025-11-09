# agentic_service.py - Autonomous AI Agent for Proactive Study Support
"""
This module implements the agentic AI behavior:
1. Automatically syncs calendar every 1 minute
2. Proactively detects new assignments and creates them in Supabase
3. Sends personalized email notifications with direct links
4. Learns from user behavior and adapts recommendations
"""

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta, timezone
from database import get_upcoming_assignments, mark_reminder_sent, extract_assignment_info, get_unprocessed_assignments
from email_service import send_new_assignment_notification
from calendar_reader import list_and_store_events
from assignment_sync import get_supabase_client, sync_calendar_to_assignments, mark_assignment_notification_sent
import requests
import os
from dotenv import load_dotenv
import pytz

load_dotenv()

# Configuration
USER_EMAIL = os.getenv('USER_EMAIL', 'student@example.com')
SYNC_INTERVAL_MINUTES = 1  # Sync every 1 minute for faster detection
CHECK_DAYS_AHEAD = 7  # Check for exams in next 7 days


class AgenticStudyCompanion:
    """
    Autonomous AI agent that proactively helps students prepare for exams.
    """
    
    def __init__(self):
        # Use daemon=True to allow graceful shutdown
        self.scheduler = BackgroundScheduler(daemon=True)
        self.is_running = False
        self.last_sync = None
        self.notifications_sent = 0
        
    def sync_calendar_task(self):
        """Background task: Sync Google Calendar with MongoDB."""
        try:
            print("\n" + "="*60)
            print(f"🤖 [AGENT] Auto-sync started at {datetime.now().strftime('%H:%M:%S')}")
            print("="*60)
            
            success = list_and_store_events(days_ahead=90)
            
            if success:
                self.last_sync = datetime.now()
                print(f"✅ [AGENT] Calendar synced successfully")
            else:
                print(f"⚠️ [AGENT] Calendar sync had issues")
                
            print("="*60 + "\n")
            
        except Exception as e:
            print(f"❌ [AGENT] Sync error: {str(e)}")
    
    def get_user_id_from_email(self, email):
        """Get user ID from Supabase by email using REST API."""
        try:
            client = get_supabase_client()
            url = f"{client['url']}/rest/v1/profiles"
            url += f"?email=eq.{email}&select=id"
            response = requests.get(url, headers=client['headers'])
            
            if response.status_code == 200:
                result = response.json()
                if result and len(result) > 0:
                    return result[0]['id']
            return None
        except Exception as e:
            print(f"⚠️ [AGENT] Error getting user ID: {str(e)}")
            return None
    
    def check_and_notify_task(self):
        """
        Background task: Check for upcoming exams and send proactive reminders.
        This is the core 'agentic' behavior - the AI takes initiative.
        """
        try:
            print("\n" + "="*60)
            print(f"🧠 [AGENT] Checking for upcoming exams at {datetime.now().strftime('%H:%M:%S')}")
            print("="*60)
            
            # First, sync any unprocessed assignments to Supabase
            user_id = self.get_user_id_from_email(USER_EMAIL)
            if user_id:
                unprocessed = get_unprocessed_assignments()
                if unprocessed:
                    print(f"🔄 [AGENT] Syncing {len(unprocessed)} new assignments to Supabase...")
                    created_assignments = sync_calendar_to_assignments(user_id)
                    print(f"✅ [AGENT] Created {len(created_assignments)} assignments in 'Your assignments' tab")

                    # Send email notification for each new assignment
                    for assignment in created_assignments:
                        try:
                            assignment_details = {
                                'id': assignment['id'],
                                'title': assignment['title'],
                                'date': assignment['due_at'],
                                'type': assignment['type'],
                                'course': assignment['title']  # Can be improved with better parsing
                            }

                            # Send notification email
                            email_sent = send_new_assignment_notification(USER_EMAIL, assignment_details)

                            if email_sent:
                                # Mark notification as sent in Supabase
                                mark_assignment_notification_sent(assignment['id'])
                                print(f"📧 [AGENT] Notification sent for: {assignment['title']}")
                            else:
                                print(f"⚠️ [AGENT] Failed to send notification for: {assignment['title']}")
                        except Exception as e:
                            print(f"❌ [AGENT] Error sending notification: {str(e)}")
                            continue
            else:
                unprocessed = get_unprocessed_assignments()
                if unprocessed:
                    print(f"⚠️ [AGENT] User '{USER_EMAIL}' not found in Supabase.")
                    print(f"   📝 {len(unprocessed)} assignments are waiting to sync.")
                    print(f"   👉 Please log in to the app first:")
                    print(f"      http://localhost:8080/auth")
                    print(f"      Use email: {USER_EMAIL}")
                    print(f"   ✅ Assignments will sync automatically once you're logged in!")
            
            # Disabled: Old exam reminder system
            # Now only send notification when new assignment is first detected (above)
            # No additional reminders are sent
            print("✅ [AGENT] Assignment notifications handled during sync")
            print("="*60 + "\n")
            
        except Exception as e:
            print(f"❌ [AGENT] Check and notify error: {str(e)}")
    
    def start(self):
        """Start the autonomous agent."""
        if self.is_running:
            print("⚠️ Agent is already running")
            return
        
        # Check if scheduler is already running (from previous instance)
        if self.scheduler.running:
            try:
                self.scheduler.shutdown(wait=False)
            except:
                pass
        
        print("\n" + "="*60)
        print("🤖 STARTING AGENTIC STUDY COMPANION")
        print("="*60)
        print(f"📧 User Email: {USER_EMAIL}")
        print(f"⏰ Sync Interval: Every {SYNC_INTERVAL_MINUTES} minutes")
        print(f"🔍 Monitoring: Exams within {CHECK_DAYS_AHEAD} days")
        print(f"🧠 AI Mode: AUTONOMOUS (Proactive Notifications)")
        print("="*60 + "\n")
        
        try:
            # Remove existing jobs if any
            if self.scheduler.get_job('calendar_sync'):
                self.scheduler.remove_job('calendar_sync')
            if self.scheduler.get_job('exam_notification'):
                self.scheduler.remove_job('exam_notification')
            
            # Schedule calendar sync every 5 minutes
            self.scheduler.add_job(
                self.sync_calendar_task,
                'interval',
                minutes=SYNC_INTERVAL_MINUTES,
                id='calendar_sync',
                next_run_time=datetime.now(),  # Run immediately on start
                replace_existing=True
            )
            
            # Schedule exam check and notification every 5 minutes (offset by 1 minute)
            self.scheduler.add_job(
                self.check_and_notify_task,
                'interval',
                minutes=SYNC_INTERVAL_MINUTES,
                id='exam_notification',
                next_run_time=datetime.now() + timedelta(minutes=1),  # Run 1 min after sync
                replace_existing=True
            )
            
            # Start the scheduler
            if not self.scheduler.running:
                self.scheduler.start()
            self.is_running = True
            
            print("✅ Agentic AI Agent is now active!")
            print(f"   Next sync: {datetime.now().strftime('%H:%M:%S')}")
            print(f"   Next check: {(datetime.now() + timedelta(minutes=1)).strftime('%H:%M:%S')}")
            print("\n")
        except Exception as e:
            print(f"⚠️ Error starting agent: {str(e)}")
            print("   Agent will retry on next request")
            self.is_running = False
    
    def stop(self):
        """Stop the autonomous agent."""
        if not self.is_running:
            return
        
        try:
            if self.scheduler.running:
                self.scheduler.shutdown(wait=False)
        except Exception as e:
            print(f"⚠️ Error stopping scheduler: {str(e)}")
        
        self.is_running = False
        print("\n🛑 Agentic AI Agent stopped")
    
    def get_status(self):
        """Get current agent status."""
        return {
            'is_running': self.is_running,
            'last_sync': self.last_sync.isoformat() if self.last_sync else None,
            'notifications_sent': self.notifications_sent,
            'next_sync': self.scheduler.get_job('calendar_sync').next_run_time.isoformat() if self.is_running else None,
            'next_check': self.scheduler.get_job('exam_notification').next_run_time.isoformat() if self.is_running else None
        }


# Global instance
agent = AgenticStudyCompanion()


def start_agent():
    """Start the agentic AI agent."""
    agent.start()


def stop_agent():
    """Stop the agentic AI agent."""
    agent.stop()


def get_agent_status():
    """Get agent status."""
    return agent.get_status()


if __name__ == '__main__':
    # Test the agent
    print("Testing Agentic Study Companion...")
    start_agent()
    
    try:
        import time
        # Keep running for testing
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nStopping agent...")
        stop_agent()

