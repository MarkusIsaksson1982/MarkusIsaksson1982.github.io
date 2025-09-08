# Ethical AI & Cyber Safety Learning Hub

_A showcase of AI-accelerated full-stack development with Next.js, Supabase, and Tailwind CSS._

**Project Status: Completed (v0.1.0)**

[**Live Demo (Placeholder)**](https://your-deployment-link.com)

---

## 📖 Overview

The Ethical AI & Cyber Safety Learning Hub is a full-stack web application designed to educate users on critical modern-day topics through an interactive and engaging platform. This project was built to demonstrate a highly efficient, AI-accelerated development workflow, where a human developer acts as the architect and an AI assistant (like me) serves as a co-developer, handling boilerplate, component generation, and implementation details.

The result is a feature-rich, secure, and scalable application built in a fraction of the time of traditional development, showcasing mastery of modern web technologies and a strategic approach to using AI as a productivity force-multiplier.

---

## ✨ Key Features

This application includes a complete set of features that form a cohesive and valuable user experience:

*   **User Authentication**: Secure sign-up (with email confirmation), login, and session management powered by Supabase Auth.
*   **Protected Routes**: Core content like the quiz and user dashboard are only accessible to authenticated users.
*   **Interactive Quiz**: A dynamic quiz with questions and answers fetched from the database. The user's state is managed on the client, and results are persisted.
*   **Personalized Dashboard**: A dedicated, protected page for users to view their past quiz scores and track their progress over time.
*   **Gamification with a Public Leaderboard**: A public page displaying the top 10 highest scores from all users, powered by an efficient PostgreSQL function for data aggregation.
*   **Dynamic Content Hub**: A "Resources" page that fetches and displays a curated list of articles and guides from the database, acting as a simple CMS.
*   **User Feedback System**: A public-facing form that allows any user to submit feedback, which is securely saved to the database using a Next.js Server Action.
*   **Modern UI/UX**: A fully responsive and accessible interface built with Tailwind CSS and shadcn/ui, including light and dark modes.

---

## 🛠️ Tech Stack

This project was built with a modern, integrated tech stack chosen for its developer experience and performance.

*   **Core Framework:** **Next.js** (App Router)
*   **Styling:** **Tailwind CSS** + **shadcn/ui**
*   **Backend & Database:** **Supabase** (Postgres, Auth, Database Functions)
*   **State Management:** **React State** (`useState`) for component-level state and **Server Actions** for form handling.
*   **Deployment:** Vercel (Recommended)

---

## 🚀 The AI-Accelerated Workflow in Action

This project is a testament to a new paradigm of software development. The human developer served as the project lead, architect, and quality assurance, while the AI assistant executed on well-defined tasks with speed and precision.

**The process was simple and effective:**

1.  **High-Level Prompting**: The developer provided a clear goal (e.g., "Create the login page UI using shadcn/ui components").
2.  **AI-Powered Scaffolding**: The AI assistant generated the complete, high-quality code for the component (`app/login/page.tsx`), including all necessary imports and styling.
3.  **Server-Side Logic Generation**: The developer requested the backend logic (e.g., "Implement a Server Action to handle login with Supabase"). The AI generated the `actions.ts` file with secure, server-side code.
4.  **Integration and Review**: The developer reviewed the generated code, requested minor adjustments, and integrated it into the main application.

This iterative loop—**Prompt, Generate, Integrate, Review**—was applied to every feature, from the initial project setup to the complex leaderboard logic, dramatically reducing development time while enforcing best practices.

---

## 🏃‍♂️ Getting Started

To run this project locally, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/ethical-ai-hub.git
    cd ethical-ai-hub/v0.1.0
    ```

2.  **Install dependencies:**
    ```bash
    npm install
    ```

3.  **Set up your environment variables:**
    *   Create a file named `.env.local` in the `v0.1.0/` directory.
    *   Add your Supabase project credentials:
        ```env
        NEXT_PUBLIC_SUPABASE_URL=your-supabase-url
        NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key
        ```

4.  **Set up the Supabase database:**
    *   In your Supabase project's SQL Editor, run the SQL scripts to create the `questions`, `quiz_results`, `resources`, `feedback`, and `get_leaderboard` function. You can find these scripts in our chat history.

5.  **Run the development server:**
    ```bash
    npm run dev
    ```

The application will be available at `http://localhost:3000`.

---

## 📝 License

This project is licensed under the **MIT License**. See the `LICENSE` file for details.
