# Product Requirements Document (PRD)
## AI-Powered Physics Visualization Platform

---

## Executive Summary

Building an educational web application that automatically converts natural language physics problems into interactive visual simulations and animated explanations. Students can ask questions like "A boat crosses a river at 5 m/s, river flows at 3 m/s - show me what happens" and receive both animated explanations and interactive simulations where they can manipulate parameters in real-time.

---

## Core Vision

**Problem:** Physics concepts (relative motion, projectile motion, vectors, forces) are abstract and hard to visualize from text/equations alone.

**Solution:** AI generates custom visualizations for each question - combining:
- Animated video explanations (Manim)
- Interactive browser simulations (p5.js/Three.js)
- Optional realistic renders for premium users (Blender)

**Key Innovation:** Using self-hosted SLMs keeps marginal costs near zero, making this scalable for thousands of students.

---

## Technical Architecture Pipeline

### User Flow
```
User Input (Natural Language Question)
    ↓
SLM Analysis (Extract parameters, classify problem type)
    ↓
Code Generation (Manim/p5.js/Three.js/Blender scripts)
    ↓
Execution & Rendering
    ↓
Present to User (Video player + Interactive canvas + Explanation text)
```

### Detailed Pipeline

**Step 1: Question Processing**
- User submits natural language question via web interface
- Backend receives question, user tier (free/premium), problem context

**Step 2: SLM Analysis** (via Ollama)
- Extract key parameters (velocities, angles, masses, distances, etc.)
- Classify problem type (projectile motion, relative velocity, forces, optics, etc.)
- Determine visualization needs (2D vectors, 3D motion, flowing fluids, etc.)
- Decide: Manim video + p5.js interactive OR Blender hybrid (if premium + realistic needed)

**Step 3: Code Generation**
- SLM generates structured code based on templates + few-shot examples
- Output formats:
  - Manim: Python script with Scene class
  - p5.js: JavaScript with setup() and draw() functions + sliders
  - Three.js: JavaScript scene description
  - Blender: Python script using bpy API (premium only)

**Step 4: Validation & Auto-Fix Loop**
- Execute generated code in sandbox environment
- If error detected → send error back to SLM for correction
- Retry up to 2 times
- If still fails → fallback to simpler visualization or use cached template

**Step 5: Rendering**
- **Manim path:** Run `manim -qm script.py SceneName` → Get MP4
- **p5.js/Three.js path:** Send code to frontend → Renders in user's browser (instant)
- **Blender path (premium):** Run `blender --background --python script.py` → Combine with Manim overlay using FFmpeg

**Step 6: Delivery**
- Serve video via CDN/cloud storage URL
- Embed p5.js/Three.js code in iframe or canvas element
- Show text explanation + equations
- Add interactive controls (sliders for velocity, angle, mass, etc.)

---

## Technology Stack

### Frontend
- **Framework:** React.js or Next.js
- **Styling:** Tailwind CSS
- **Canvas Rendering:** p5.js for 2D, Three.js/Babylon.js for 3D
- **Video Player:** HTML5 video element
- **UI Components:** Interactive sliders, number inputs, play/pause controls

### Backend
- **Runtime:** Node.js with Express OR Python with FastAPI
- **SLM Inference:** Ollama (self-hosted)
  - Recommended models: Qwen3-8B, GLM-4-9B, Phi-4, or Qwen2.5-Coder-7B
- **Video Generation:** Manim Community Edition
- **3D Rendering (Premium):** Blender Python API
- **Video Processing:** FFmpeg (for combining Manim + Blender)
- **Deployment:** Vercel/Railway/Render for web, Hetzner/RunPod for GPU server

### Database & Storage
- **User Data:** Supabase or Firebase (auth + user tier tracking)
- **Video/Asset Storage:** Cloudinary or AWS S3
- **Caching:** Redis (for popular problem variations)

---

## Feature Tiers

### Free Tier
✅ Natural language problem input  
✅ Text explanation with equations  
✅ Manim animated video (up to 40 seconds)  
✅ Interactive p5.js/Three.js simulation with parameter sliders  
✅ Simple visual style (dots, arrows, labels - educational diagrams)  
✅ Up to 10 problems per day  

### Premium Tier (₹49-99/month or ₹399-799/year)
✅ Everything in Free  
✅ Realistic Blender renders (flowing water, realistic lighting, physics sims)  
✅ Longer animations (up to 2 minutes)  
✅ Priority queue (faster generation)  
✅ Download videos  
✅ Unlimited problems  
✅ Ad-free experience  

---

## Phases of Development

### Phase 1: MVP Foundation (Week 1-2)
**Goal:** Prove core concept with one physics topic

**Tasks:**
1. Set up Ollama with Qwen2.5-Coder-7B or similar SLM
2. Create prompt template with 3 few-shot examples for projectile motion
3. Build simple backend API endpoint:
   - Accept question → Call Ollama → Get Manim code
4. Set up Manim rendering pipeline (headless)
5. Build minimal frontend:
   - Input box
   - Text explanation display
   - Video player
6. Test end-to-end with 5 projectile motion variations

**Success Criteria:**
- User asks "ball thrown upward at 10 m/s" → Gets working Manim video in <60 seconds
- 80%+ success rate on first code generation attempt

**Clarifications Needed:**
- Which physics topic should we start with? (Projectile motion, river boat, or something else?)
- Do you have GPU access for Manim rendering, or should we optimize for CPU-only?
- What's your preferred backend language: Python (FastAPI) or Node.js?

---

### Phase 2: Interactive Simulations (Week 3)
**Goal:** Add real-time browser-based interactivity

**Tasks:**
1. Extend prompt template to generate p5.js code
2. Build interactive canvas component:
   - Embedded p5.js sketch
   - Sliders for velocity, angle, mass
   - Real-time parameter updates
3. SLM generates both Manim (video explanation) AND p5.js (interactive)
4. Add 3 more physics topics:
   - River boat (relative velocity)
   - Inclined plane (forces)
   - Simple pendulum (harmonic motion)

**Success Criteria:**
- User gets both video + interactive sim
- Sliders update simulation in real-time (<50ms latency)
- Works on mobile and desktop browsers

**Clarifications Needed:**
- Should p5.js and Manim both generate for every question, or let SLM decide which is better?
- Any preference between p5.js (easier 2D) vs Three.js (better 3D but steeper)?

---

### Phase 3: Error Handling & Robustness (Week 4)
**Goal:** Make system production-ready

**Tasks:**
1. Implement auto-fix loop:
   - Run generated code in sandbox (Docker container)
   - Capture errors → Send to SLM for correction
   - Retry up to 2 times
2. Add fallback templates for common failures
3. Build caching layer:
   - Hash question + parameters
   - Store rendered videos in S3/Cloudinary
   - Serve cached version if same question asked
4. Add 5 more physics topics (optics, circuits, collisions, etc.)
5. Load testing: Ensure handles 100 concurrent requests

**Success Criteria:**
- 95%+ problems get valid visualization (with auto-fix)
- Cache hit rate >60% for popular problems
- Average response time <30 seconds

**Clarifications Needed:**
- Which hosting platform do you prefer for the backend?
- Budget for cloud storage (S3 vs Cloudinary)?

---

### Phase 4: Premium Features - Blender Integration (Week 5-6)
**Goal:** Add realistic renders for paid users

**Tasks:**
1. Create Blender script templates for:
   - Flowing river (fluid sim or animated texture)
   - Projectile with realistic gravity & lighting
   - Collision with deformation
2. Implement hybrid pipeline:
   - Manim generates vectors/labels (transparent overlay)
   - Blender generates realistic base scene
   - FFmpeg combines both
3. Add premium tier detection in backend
4. Build payment integration (Razorpay/Stripe)
5. Show "upgrade to premium" CTA for realistic renders

**Success Criteria:**
- Premium users get cinematic quality renders
- Hybrid videos look cohesive (Manim + Blender blend well)
- Payment flow works end-to-end

**Clarifications Needed:**
- Do you already have a payment gateway preference (Razorpay for India)?
- Should Blender run on same server as Manim, or separate GPU instance?
- Monthly/yearly pricing preference?

---

### Phase 5: UI/UX Polish & Launch (Week 7-8)
**Goal:** Production-ready, delightful user experience

**Tasks:**
1. Redesign UI with proper visual hierarchy:
   - Clean input area
   - Split-screen: video left, interactive right
   - Mobile-responsive layout
2. Add features:
   - Problem history (saved visualizations)
   - Share button (social media, WhatsApp)
   - Download video option
   - Light/dark mode
3. Build landing page with demo videos
4. Add analytics (Mixpanel/PostHog)
5. Beta test with 50-100 students from Telangana
6. Fix bugs, optimize performance
7. Launch on Product Hunt / Reddit / EdTech communities

**Success Criteria:**
- Beta users rate app 4.5+ / 5
- <5% bounce rate on landing page
- Students share with friends (organic growth)

**Clarifications Needed:**
- Do you have beta testers lined up, or should we plan recruitment?
- Target launch date for the hackathon?

---

## Cost Analysis

### Monthly Operating Costs (Estimated)

| Item | Free Tier (0-1000 users) | Growth (1000-10K users) |
|------|-------------------------|------------------------|
| **GPU Server** (Hetzner/RunPod) | ₹12,000 | ₹12,000-24,000 |
| **SLM (Ollama)** | ₹0 (self-hosted) | ₹0 |
| **Storage (S3/Cloudinary)** | ₹500-1,500 | ₹3,000-8,000 |
| **Backend Hosting** | ₹0-500 (Vercel free) | ₹2,000-5,000 |
| **Manim Rendering** | Included in GPU | Included in GPU |
| **Blender (Premium only)** | N/A | Same GPU server |
| **Total** | **~₹12,500-14,000** | **~₹17,000-37,000** |

**Key Insight:** Fixed cost model! Once you have the GPU server, marginal cost per user is near zero.

---

## Prompt Engineering Strategy

### SLM Prompt Template (Critical for Success)

```markdown
You are an expert physics animation code generator.
You ONLY generate clean, correct, minimal code.
Never add comments unless asked. Never explain. Just output the code.

STRICT RULES:
- Represent objects as dots/circles with labels (NO realistic cars, people, bikes)
- Use standard colors: blue=environment forces, red=object velocity, green=resultant
- Keep scenes simple, clean, educational
- Animation duration: 20-40 seconds
- Always include Wait() at important steps for pacing

PHYSICS FACTS (use exactly):
{{physics_formulas_for_topic}}

TASK:
User problem: "{{user_question}}"

Extract these parameters:
{{parameter_list}}

Then generate {{target_library}} code for an educational animation showing:
- Motion clearly with labeled vectors
- Key equations appearing step-by-step
- Trajectory/path visualization

OUTPUT FORMAT: Only code inside ```python ... ```

EXAMPLES:
{{few_shot_examples}}
```

### Few-Shot Examples (Store 2-3 per topic)
- Example 1: Projectile motion - standard case
- Example 2: Projectile motion - at an angle
- Example 3: River boat - crossing straight

---

## Critical Questions for You

Before Claude Code starts building, please clarify:

### Technical Setup
1. **Which SLM model do you want to use with Ollama?** (Recommendation: Qwen2.5-Coder-7B or Qwen3-8B)
2. **Backend language preference:** Python (FastAPI) or Node.js (Express)?
3. **Do you have GPU access?** (Affects Manim render speed)
4. **Hosting preference:** Vercel, Railway, Render, or self-hosted VPS?

### Product Scope
5. **Which physics topics should we prioritize for MVP?** (Pick 3-5 from: projectile motion, river boat, inclined plane, circular motion, optics, circuits, pendulum, collisions)
6. **Should we build premium tier in Phase 4, or save it for post-hackathon?**
7. **Target users:** High school (Class 9-12) or college-level physics?

### Hackathon Specifics
8. **Hackathon deadline?** (This determines if we do all 5 phases or focus on Phase 1-3)
9. **Demo requirements:** Just a working prototype, or polished UI needed?
10. **Team size:** Are you building solo, or do you have teammates for frontend/design?

---

## Success Metrics

### For Hackathon Demo
- ✅ Can demonstrate 5+ different physics problems getting visualized
- ✅ Interactive simulations work smoothly in browser
- ✅ Generation time <60 seconds per problem
- ✅ Clean, professional UI that judges can understand in 2 minutes

### Post-Launch (3 months)
- 1,000+ students using the platform
- 80%+ problems successfully visualized on first try
- 15-20% conversion to premium tier
- 4.5+ star rating from users

---

## Next Steps

**Immediate Actions:**
1. **Answer the clarification questions above**
2. **Set up Ollama** with your chosen SLM model
3. **Install Manim:** `pip install manim`
4. **Clone starter repo structure** (Claude Code will generate this)
5. **Start with Phase 1 MVP** - prove the core concept works

Once you provide clarifications, Claude Code can:
- Generate complete project structure
- Write backend API code
- Create SLM prompt templates with examples
- Build frontend components
- Set up Docker containers for sandboxed execution
- Configure Manim rendering pipeline

---

## Questions for Claude Code

When you start building, Claude Code will need to know:

**Project Setup:**
- Should I create a monorepo (frontend + backend together) or separate repos?
- Do you want Docker for local development, or direct installation?
- Should I include deployment configs (Dockerfile, docker-compose.yml)?

**Code Preferences:**
- TypeScript or JavaScript for frontend?
- Prefer class components or functional components in React?
- Want ESLint/Prettier configured?

**Testing:**
- Should I include unit tests (Jest/Vitest)?
- E2E tests (Playwright)?

**Please answer the critical questions above so Claude Code has full clarity to start building! 🚀**
