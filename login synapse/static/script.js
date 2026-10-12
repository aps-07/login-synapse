
"use strict";

// HTML elements
const loginPage = document.getElementById("loginPage");
const loginForm = document.getElementById("loginForm");
const message = document.getElementById("message");

const dashboard = document.getElementById("dashboard");
const welcomeMessage = document.getElementById("welcomeMessage");
const roleMessage = document.getElementById("roleMessage");
const dashboardCards = document.getElementById("dashboardCards");

const logoutBtn = document.getElementById("logoutBtn");

const adminUsersSection =
    document.getElementById("adminUsersSection");
const usersSectionEyebrow =
    document.getElementById("usersSectionEyebrow");
const usersSectionDescription =
    document.getElementById("usersSectionDescription");
const usersAccessBadge =
    document.getElementById("usersAccessBadge");

const usersMessage = document.getElementById("usersMessage");
const usersList = document.getElementById("usersList");


// Communicate with the Flask backend
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


// Clear the user directory
function clearUsers() {
    usersList.replaceChildren();
    usersMessage.textContent = "";
    usersMessage.className = "users-message";
}


// Show the correct dashboard for each role
function showDashboard(user) {
    loginPage.style.display = "none";
    dashboard.style.display = "block";

    welcomeMessage.textContent = `Welcome, ${user.email}`;
    roleMessage.textContent =
        `You are logged in as ${user.role.toUpperCase()}.`;

    dashboardCards.replaceChildren();

    // Admin dashboard
    if (user.role === "admin") {
        addCard(
            "Admin Dashboard",
            "You have administrator access to Synapse."
        );

        addCard(
            "User Directory",
            "View all registered accounts."
        );

        addCard(
            "Administration",
            "Access admin-only controls."
        );

        adminUsersSection.style.display = "block";
        usersSectionEyebrow.textContent = "ADMINISTRATION";
        usersSectionDescription.textContent =
            "Review accounts registered in this application.";
        usersAccessBadge.textContent = "ADMIN ACCESS";

        loadUsers("/api/admin/users");
    }

    // Manager dashboard
    else if (user.role === "manager") {
        addCard(
            "Manager Dashboard",
            "Welcome to your manager workspace."
        );

        addCard(
            "User Directory",
            "View all registered users and their roles."
        );

        addCard(
            "Team Overview",
            "Review the accounts available in Synapse."
        );

        adminUsersSection.style.display = "block";
        usersSectionEyebrow.textContent = "MANAGEMENT";
        usersSectionDescription.textContent =
            "You can view accounts but cannot access admin controls.";
        usersAccessBadge.textContent = "VIEW ONLY";

        loadUsers("/api/manager/users");
    }

    // Regular user dashboard
    else {
        addCard(
            "User Dashboard",
            "Welcome to your personal workspace."
        );

        addCard(
            "My Profile",
            `You are logged in with ${user.email}.`
        );

        adminUsersSection.style.display = "none";
        clearUsers();
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
            body: JSON.stringify({ email, password })
        });

        showDashboard(user);
        loginForm.reset();

    } catch (error) {
        message.textContent = error.message;
        message.className = "error";

    } finally {
        submitButton.disabled = false;
        submitButton.textContent = "Sign in to your account";
    }
});


// Load users from the correct role-protected endpoint
async function loadUsers(endpoint) {
    clearUsers();

    usersMessage.textContent = "Loading users...";

    try {
        const data = await apiRequest(endpoint);

        data.users.forEach(function (user) {
            const item = document.createElement("li");

            const details = document.createElement("span");
            details.textContent = user.email;

            const role = document.createElement("span");
            role.className = "role-tag";
            role.textContent = user.role.toUpperCase();

            item.append(details, role);
            usersList.appendChild(item);
        });

        usersMessage.textContent = data.users.length === 0
            ? "No users found."
            : `${data.users.length} account(s) found.`;

    } catch (error) {
        usersMessage.textContent = error.message;
        usersMessage.className = "users-message error";
    }
}


// Restore an existing session after page refresh
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

        adminUsersSection.style.display = "none";
        clearUsers();
        dashboardCards.replaceChildren();

    } catch (error) {
        alert(error.message);

    } finally {
        logoutBtn.disabled = false;
    }
});


// Start the application
restoreSession();
