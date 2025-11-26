Overview

This document defines the agents, their roles, responsibilities, and communication rules for a multi-agent Codex environment.
Each agent focuses on a specific competency: security, code quality, architecture, optimisation, documentation, and testing.
All agents follow a strict chain-of-thought isolation rule: no agent may reveal reasoning—only final outputs.

Agents
1. SecurityAgent

Primary Goal:
Ensure the system is cryptographically sound, leak-proof, and resistant to abuse.

Responsibilities:

Audit code for vulnerabilities: input validation, injection, crypto misuse, privilege escalation.

Enforce secure defaults (Argon2id, AES-GCM, HMAC-SHA512,

You said:
no basicaaly just background knowledge of this questai

ChatGPT said:

Got you — you just want an agents.md file that gives ChatGPT Codex background knowledge about QuestAI, not multi-agent instructions.

Here’s a clean, simple, Codex-ready agents.md that summarises QuestAI’s full context so any code-generation agent knows what the project is, what it does, and what features it must support.

agents.md — QuestAI Background Context
What QuestAI Is

QuestAI is a gamified, AI-powered learning platform designed for primary and high-school students. Its purpose is to make studying more engaging by turning learning into an adventure with quests, levels, points, streaks, rewards, leaderboards, and adaptive question difficulty.

The platform uses real-time AI personalisation to adjust lesson difficulty, generate unique questions, and target student weaknesses. It works across multiple subjects and aims to boost motivation and improve learning efficiency.

Core Features

Adaptive AI Learning:
Automatically adjusts question difficulty based on performance and history.

Gamification System:
Points, levels, badges, streaks, daily quests, rewards, leaderboard.

Quests & Adventure Mode:
Students progress like a game while learning curriculum content.

Personalised Study Path:
Continuously updated after every question.

Progress Tracking:
Dashboards for students, teachers, and parents.

Cross-Device Access:
Works on phone, tablet, and desktop.

Target Users

Primary school students (8–12)

High-school students (13–18)

Students needing motivation

Parents wanting modern learning tools

Schools adopting digital education

Demographic assumptions: Australia-first release, middle-income households, expansion later.

Competitors & Market Gap

Duolingo: Gamified but limited to language learning.

Khan Academy: Adaptive but not gamified.

Mathletics: Curriculum-focused but less adaptive.

Quizlet: Revision-based, no adventure system.

QuestAI fills the gap by combining:
✔ Adaptive learning
✔ Full gamification
✔ Curriculum content
✔ Adventure-style progression

No major platform currently merges all four.

Business & Productivity Model

Cloud-based backend to reduce hardware cost.

Automated systems generate questions, track users, and adjust difficulty.

Small development team structure (devs, designers, support).

Trello/Slack workflow method for internal management.

Potential revenue streams: freemium model, school licensing, subscriptions.

SWOT Summary

Strengths:

High engagement

AI-personalised learning

Unique gamification layer

Wide device compatibility

Weaknesses:

Requires stable internet

Cost of ongoing updates

Needs initial user base

Opportunities:

Growing ed-tech market

School partnerships

Global expansion

Multiplayer quests in the future

Threats:

Strong competitors

Rapid tech changes

Privacy/compliance risk

Limited school budgets

Why Online Presence Is Required

AI processing relies on cloud models

Syncing progress across devices

Parents/teachers dashboards

Faster delivery of updates and new features

Industry standards from competitors

High-Level Vision

QuestAI aims to transform education by blending adaptive AI with video-game-style engagement to create a learning experience that is addictive, personalised, and academically effective.

Tagline:
Learn Smarter. Play Harder.
