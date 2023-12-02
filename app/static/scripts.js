/**
 * We're going to hide the sign up page if the user is already a member
 * We're going to hide login page if the user is not a member
 */


'use strict';
/**Sign up button */
const signBtn = document.querySelector('.sign-up-button');
/**Login Div */
const loginDiv = document.querySelector('login');
/**Sign up Div */
const signDiv = document.querySelector('.sign-up');
signBtn.addEventListener('click',signup);

function signup(){
    /**Show the signUp div instead of the login */
    loginDiv.classList.add('hidden');
    signDiv.classList.remove('hidden');

}