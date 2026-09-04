# 🗂️ Portfolio Generator

A web portfolio generator to create and manage user portfolios with their associated projects.

🔗 **Live Demo** : [https://web-portfolio-generator.onrender.com/](https://web-portfolio-generator.onrender.com/)

---

## 📋 Features

- **User management** : Create and delete users (name, first name, age, email, GitHub, phone number)
- **Project management** : Dynamically add multiple projects to a user (name, description, image, link, skill list)
- **CV / Portfolio** : Automatic portfolio page generation for each user with a project carousel
- **Reactive interface** : Uses HTMX for dynamic interactions without page reload
- **Database** : Data persistence via SQLite with SQLModel

---

## 🛠️ Tech Stack

| Technology | Role |
|---|---|
| **FastAPI** | Backend / REST API |
| **SQLModel + SQLite** | Database |
| **Jinja2** | HTML templating engine |
| **HTMX** | Dynamic client-side interactions |
| **Simple.css** | Minimal CSS styling |
| **JavaScript** | Add user form handling |

---

## 🚀 Local Installation (Windows)

### Prerequisites

- [Python 3.10+](https://www.python.org/downloads/) installed on your machine
- `pip` available in your terminal

### Steps

**1. Clone the repository**

```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

**2. Create a virtual environment**

```bash
python -m venv venv
```

**3. Activate the virtual environment**

```bash
venv\Scripts\activate
```

> You should see `(venv)` appear at the beginning of your command line.

**4. Install dependencies**

```bash
pip install -r requirements.txt
```

**5. Start the server**

```bash
fastapi run --reload
```

**6. Open in your browser**

Go to : [http://127.0.0.1:8000](http://127.0.0.1:8000)

---


## 📖 Usage

1. **Home page** (`/`) : Lists all registered users
   - Click 📄 to view a user's portfolio
   - Click ❌ to delete a user (and their projects)

2. **Add a user** (`/add-user-page`) : Form to create a user and their projects
   - Fill in the personal information
   - Add one or more projects using the **"Add project"** button
   - Submit the form to create everything

3. **Portfolio** (`/cv/{user_id}`) : Automatically generated portfolio page with a project carousel

---

## 🌐 Deployment

The application is deployed on **Render** and accessible here :

👉 [https://web-portfolio-generator.onrender.com/](https://web-portfolio-generator.onrender.com/)

---

## 🤖 AI Assistance

This project has used **Claude Code (Sonnet 5.0)** as a coding agent to assist with development.
