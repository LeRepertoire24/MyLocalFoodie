//--------------------------------------//
//       static/js/auth/Oauth.js        //
//--------------------------------------//

// Utility to check if the user is authenticated
function isAuthenticated() {
    return !!sessionStorage.getItem('access_token');
}

//--------------------------------------//
//      Utility to clear the session    //
//--------------------------------------//
function clearSession() {
    sessionStorage.clear();
    window.location.href = '/auth/login'; // Redirect to login
}
//-----------------------------------------------------//
//        Add an event listener for logout button      //
//-----------------------------------------------------//
document.addEventListener('DOMContentLoaded', function () {
    const logoutButton = document.querySelector('#logout');

    if (logoutButton) {
        logoutButton.addEventListener('click', function () {
            clearSession();
        });
    }
});
//----------------------------------------------//
//     Function to initialize Google Sign-In    //
//----------------------------------------------//
function initializeGoogleSignIn() {
    gapi.load('auth2', function() {
        const auth2 = gapi.auth2.init({
            client_id: '{{ GOOGLE_CLIENT_ID }}',  // From Google Developer Console
            scope: 'https://www.googleapis.com/auth/calendar https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/tasks.readonly'
        });
        //-----------------------------------------------------//
        //       Add event listener for the sign-in button     //
        //-----------------------------------------------------//
        document.getElementById('sign-in-btn').addEventListener('click', function() {
            // Trigger Google OAuth sign-in
            auth2.signIn().then(function(googleUser) {
                const id_token = googleUser.getAuthResponse().id_token;
                const payroll_id = document.getElementById('username').value;  // Assume payroll_id is entered in the username field

                fetch('/auth/google/callback', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').getAttribute('content'),  // CSRF protection
                    },
                    body: JSON.stringify({ id_token: id_token, payroll_id: payroll_id })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        sessionStorage.setItem('access_token', id_token); // Store token in session
                        window.location.href = '/dashboard'; // Redirect to dashboard
                    } else {
                        alert('Error logging in: ' + data.message);
                    }
                }).catch(function(error) {
                    console.error("Google Sign-In Error:", error);
                });
            }).catch(function(error) {
                console.error("Google Sign-In Error:", error);
            });
        });
    });
}
//----------------------------------------------------------------------//
//      Initialize the Google Sign-In once the document is ready        //
//----------------------------------------------------------------------//
document.addEventListener('DOMContentLoaded', initializeGoogleSignIn);
