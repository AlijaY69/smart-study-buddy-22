# Smart Study Buddy

An intelligent AI-powered study companion that automatically detects assignments from your Google Calendar and generates personalized study sessions with adaptive exercises.

## Running the project
In the main project directory run:
```bash
docker compose up --build
```

## Features

### Automatic Assignment Detection
- Syncs with Google Calendar every 60 seconds to detect exam and assignment events
- Automatically identifies assignments using keywords (exam, test, quiz, assignment, etc.)
- Filters out study sessions to avoid duplicate detection

### AI-Powered Question Generation
- Generates exercises from your uploaded study materials using OpenAI GPT-4
- Creates 12 diverse exercises per study session across three cognitive tiers
- Questions are based on actual material content, not generic keywords

### Three-Tier Question Framework

**Tier 1: Basic Recall (40% - 5 exercises)**
- Multiple choice questions
- True/False statements
- Flashcards
- Fill-in-the-blank
- Numerical problems

**Tier 2: Understanding (30% - 4 exercises)**
- Short answer (Define)
- Short answer (Explain)
- Short answer (Compare and contrast)

**Tier 3: Application (30% - 3 exercises)**
- Scenario-based application
- Scenario-based prediction
- Error identification
- Mini problem sets

### Smart Study Scheduling
- Automatically schedules 2-4 study sessions before assignment due dates
- Integrates with Google Calendar to avoid scheduling conflicts
- Respects user's preferred study times (morning, afternoon, or evening)
- Creates Google Calendar events for each study session

### Material-Aware Learning
- Questions generated from actual uploaded content (lecture slides, notes, textbooks)
- Analyzes and extracts key concepts from study materials
- Provides contextual explanations based on your materials

### Progress Tracking
- Tracks completion status for all exercises
- Records user answers and evaluates correctness
- Immediate feedback with detailed explanations

### Email Notifications
- Sends notification when new assignment is detected
- Prompts user to upload study materials
- Direct links to assignment pages

## Tech Stack

### Frontend
- **React 18** with TypeScript
- **Vite** for build tooling
- **Tailwind CSS** for styling
- **shadcn/ui** for UI components
- **Supabase client** for authentication and database
- **React Router** for navigation
- **OpenAI** for AI question generation

### Backend
- **Python 3.8+** with Flask
- **Supabase (PostgreSQL)** for relational data storage
- **MongoDB Atlas** for calendar events storage
- **Google Calendar API** for event detection and creation
- **SendGrid** for email notifications
- **APScheduler** for background tasks

## Project Structure

```
smart-study-buddy-22/
├── backend/
│   ├── api.py                    # Flask API server
│   ├── agentic_service.py       # Background calendar sync (runs every 60s)
│   ├── assignment_sync.py       # Assignment detection and sync logic
│   ├── database.py              # MongoDB operations
│   ├── email_service.py         # SendGrid email notifications
│   ├── google_calendar.py       # Google Calendar API integration
│   ├── calendar_reader.py       # Read and store calendar events
│   ├── apply_migration.py       # Database migration helper
│   ├── reset_mongodb.py         # MongoDB reset utility
│   ├── requirements.txt         # Python dependencies
│   └── .env                     # Backend environment variables
├── src/
│   ├── components/
│   │   ├── exercises/          # Exercise component renderers
│   │   │   ├── ExerciseRenderer.tsx
│   │   │   ├── MultipleChoiceExercise.tsx
│   │   │   ├── ShortAnswerExercise.tsx
│   │   │   └── MiniProblemSetExercise.tsx
│   │   └── ui/                 # shadcn/ui components
│   ├── lib/
│   │   ├── services/
│   │   │   ├── exerciseService.ts    # Exercise generation logic
│   │   │   └── sessionService.ts     # Session management
│   │   └── templates/
│   │       ├── index.js              # Main template generator
│   │       ├── tier1_templates.js    # Tier 1 exercise templates
│   │       ├── tier2_templates.js    # Tier 2 exercise templates
│   │       └── tier3_templates.js    # Tier 3 exercise templates
│   ├── pages/
│   │   ├── Index.tsx                 # Dashboard
│   │   ├── AssignmentDetail.tsx      # Assignment & material upload
│   │   ├── SessionPage.tsx           # Study session interface
│   │   └── CalendarSync.tsx          # Manual calendar sync
│   └── main.tsx                      # Application entry point
├── supabase/
│   └── migrations/              # Database migration scripts
├── scripts/
│   ├── cleanup.py               # Code cleanup utility
│   ├── fix_empty_blocks.py      # Python syntax fixer
│   └── remove_emojis.py         # Emoji removal utility
├── .env                         # Frontend environment variables
├── package.json                 # Node.js dependencies
└── README.md                    # This file
```


## Authors
Ali Ostowar, Kacper Nizielski, Mateusz Wilk, Marc Cucias

## License

MIT License - See LICENSE file for details

## Acknowledgments

- Built with [React](https://react.dev/)
- UI components from [shadcn/ui](https://ui.shadcn.com/)
- AI powered by [OpenAI](https://openai.com/)
- Database by [Supabase](https://supabase.com/)
- Calendar integration via [Google Calendar API](https://developers.google.com/calendar)
