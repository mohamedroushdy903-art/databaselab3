/**
 * AuthGuard Database Engine (IndexedDB + Web Crypto API)
 * A real, persistent browser database that preserves user data across browser restarts.
 */

const DB_NAME = 'AuthGuardDB';
const DB_VERSION = 1;
const STORE_NAME = 'users';

// Open / Initialize IndexedDB
function openDB() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open(DB_NAME, DB_VERSION);

        request.onupgradeneeded = (event) => {
            const db = event.target.result;
            if (!db.objectStoreNames.contains(STORE_NAME)) {
                const store = db.createObjectStore(STORE_NAME, { keyPath: 'id', autoIncrement: true });
                store.createIndex('email', 'email', { unique: true });
            }
        };

        request.onsuccess = (event) => resolve(event.target.result);
        request.onerror = (event) => reject('Database error: ' + event.target.errorCode);
    });
}

// Secure Cryptographic Password Hashing using SHA-256
async function hashPassword(password) {
    const encoder = new TextEncoder();
    // Salt applied to prevent rainbow table attacks
    const data = encoder.encode(password + "_authguard_salt_2026");
    const hashBuffer = await crypto.subtle.digest('SHA-256', data);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
}

// Retrieve user by email
async function getUserByEmail(email) {
    const db = await openDB();
    return new Promise((resolve, reject) => {
        const transaction = db.transaction([STORE_NAME], 'readonly');
        const store = transaction.objectStore(STORE_NAME);
        const index = store.index('email');
        const request = index.get(email.toLowerCase().trim());

        request.onsuccess = () => resolve(request.result || null);
        request.onerror = () => reject('Failed to fetch user by email.');
    });
}

// Retrieve user by ID
async function getUserById(id) {
    const db = await openDB();
    return new Promise((resolve, reject) => {
        const transaction = db.transaction([STORE_NAME], 'readonly');
        const store = transaction.objectStore(STORE_NAME);
        const request = store.get(Number(id));

        request.onsuccess = () => resolve(request.result || null);
        request.onerror = () => reject('Failed to fetch user by ID.');
    });
}

// Register a new user in the persistent database
async function registerUser({ fullName, email, password }) {
    const cleanEmail = email.toLowerCase().trim();
    const existing = await getUserByEmail(cleanEmail);

    if (existing) {
        throw new Error('An account with this email address already exists.');
    }

    const passwordHash = await hashPassword(password);
    const now = new Date();
    const formattedDate = now.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });

    const newUser = {
        fullName: fullName.trim(),
        email: cleanEmail,
        passwordHash: passwordHash,
        createdAt: formattedDate
    };

    const db = await openDB();
    return new Promise((resolve, reject) => {
        const transaction = db.transaction([STORE_NAME], 'readwrite');
        const store = transaction.objectStore(STORE_NAME);
        const request = store.add(newUser);

        request.onsuccess = (event) => {
            newUser.id = event.target.result;
            resolve(newUser);
        };
        request.onerror = () => reject('Failed to register user to database.');
    });
}

// Authenticate user credentials
async function authenticateUser(email, password) {
    const cleanEmail = email.toLowerCase().trim();
    const user = await getUserByEmail(cleanEmail);

    if (!user) {
        throw new Error('Invalid email or password. Please try again.');
    }

    const inputHash = await hashPassword(password);
    if (user.passwordHash !== inputHash) {
        throw new Error('Invalid email or password. Please try again.');
    }

    return user;
}
