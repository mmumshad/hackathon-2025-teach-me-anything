
TechMeAnything

UX: 
Phase 1:
Website with option to chat in text/voice
When page loads for the first time check if userid exists, if not collect a unique userid from the user in a simple text box.
Super minimal web interface with a plain white background and a chat interface.
A mute toggle button in the left top corner. By default it is muted. When unmuted AI narrates whatever is on screen using Eleven labs TTS. 
A drop down menu button in the top right corner of screen (just 3 dots). Drop down to have userid. Signout option. A drop down to select languages.  
[Pass 2]: Animation character fix lottie json or so to talk to student 
User asks question, TMA replies
TMA initially asks questions about the user to understand the users background. Name, age, level of knowledge etc.
K12 student asks question, TMA replies with appropriate content
TMA asks clarifying questions to understand students knowledge level in that topic and shares a study plan to confirm that’s what student needs.
Generate video to explain any topic
First generates a script not more than 10 sentences explaining the concept
Then generates a prompt for every 1-2 sentence to create a video out of it
Generates video using Gemini or Sora 2
Generates audio narration using Eleven Labs
Plays the video and the associated audio narration at the same time
Multilingual support

Phase 2:
Generate solution to homework problem
Generates study plan in a calendar view
Generates an interactive calendar on screen with study plan for the student. 

TechStack
Backend: Python
Frontend: shadcn/next.js
ElevenLabs for audio TTS
Gemini for video gen
MEM0 for user profile & session history storage 
OpenAI as LLM
Cursor for dev
Smithery MCP 
GitHub code repo

UserProfile
UserID (UniqueKey)
Name
Grade
Language of choice

UserConversation 
User ID
DateTime
Conversation





