
"use strict";

// Get HTML elements
const loginPage = document.getElementById("loginPage");
const loginForm = document.getElementById("loginForm");
const message = document.getElementById("message");

const dashboard = document.getElementById("dashboard");
const welcomeMessage = document.getElementById("welcomeMessage");
const roleMessage = document.getElementById("roleMessage");
const dashboardCards = document.getElementById("dashboardCards");

const logoutBtn = document.getElementById("logoutBtn");

const adminUsersSection = document.getElementById("adminUsersSection");
const usersMessage = document.getElementById("usersMessage");
const usersList = document.getElementById("usersList");


// Send requests to the Flask backend
async function apiRequest(url, options = {}) {
    const response = await fetch(url, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            ...options.headers
        }
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.error || "Something went wrong.");
    }

    return data;
}


// Create a dashboard card
function addCard(title, description) {
    const card = document.createElement("div");
    card.className = "dashboard-card";

    const heading = document.createElement("h3");
    heading.textContent = title;

    const paragraph = document.createElement("p");
    paragraph.textContent = description;

    card.append(heading, paragraph);
    dashboardCards.appendChild(card);
}


// Display the correct dashboard
function showDashboard(user) {
    loginPage.style.display = "none";
    dashboard.style.display = "block";

    welcomeMessage.textContent = `Welcome, ${user.email}`;
    roleMessage.textContent =
        `You are logged in as ${user.role.toUpperCase()}.`;

    dashboardCards.replaceChildren();

    if (user.role === "admin") {
        addCard(
            "Admin Dashboard",
            "You have administrator access to the application."
        );

        addCard(
            "Manage Users",
            "View the registered users in the system."
        );

        adminUsersSection.style.display = "block";
        loadUsers();

    } else {
        addCard(
            "User Dashboard",
            "Welcome to your personal dashboard."
        );

        addCard(
            "My Profile",
            `You are logged in with the email ${user.email}.`
        );

        adminUsersSection.style.display = "none";
        usersList.replaceChildren();
        usersMessage.textContent = "";
        usersMessage.className = "";
    }
}


// Login form
loginForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    message.textContent = "";
    message.className = "";

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;

    const submitButton = loginForm.querySelector(
        'button[type="submit"]'
    );

    submitButton.disabled = true;
    submitButton.textContent = "Logging in...";

    try {
        const user = await apiRequest("/api/login", {
            method: "POST",
            body: JSON.stringify({
                email: email,
                password: password
            })
        });

        showDashboard(user);
        loginForm.reset();

    } catch (error) {
        message.textContent = error.message;
        message.className = "error";

    } finally {
        submitButton.disabled = false;
        submitButton.textContent = "Login";
    }
});


// Load registered users (admin only)
async function loadUsers() {
    usersMessage.textContent = "Loading users...";
    usersMessage.className = "";
    usersList.replaceChildren();

    try {
        const data = await apiRequest("/api/admin/users");

        usersMessage.textContent = "";

        data.users.forEach(function (user) {
            const item = document.createElement("li");

            const details = document.createElement("span");
            details.textContent = `${user.email} `;

            const role = document.createElement("span");
            role.className = "role-tag";
            role.textContent = user.role.toUpperCase();

            item.append(details, role);
            usersList.appendChild(item);
        });

        if (data.users.length === 0) {
            usersMessage.textContent = "No users found.";
        }

    } catch (error) {
        usersMessage.textContent = error.message;
        usersMessage.className = "error";
    }
}


// Restore the session after a page refresh
async function restoreSession() {
    try {
        const user = await apiRequest("/api/me");
        showDashboard(user);

    } catch (error) {
        dashboard.style.display = "none";
        loginPage.style.display = "flex";
    }
}


// Logout
logoutBtn.addEventListener("click", async function () {
    logoutBtn.disabled = true;

    try {
        await apiRequest("/api/logout", {
            method: "POST"
        });

        dashboard.style.display = "none";
        loginPage.style.display = "flex";

        loginForm.reset();

        message.textContent = "";
        message.className = "";

        usersList.replaceChildren();
        usersMessage.textContent = "";
        usersMessage.className = "";

    } catch (error) {
        alert(error.message);

    } finally {
        logoutBtn.disabled = false;
    }
});


// Start the application by checking the current session
restoreSession();