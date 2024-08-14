#Check my project -> https://cloud.mail.ru/public/MzNe/9z3RBnJ3n
I tried to make a real-time chat, this is what happened...
1) Login is carried out on the login.html window
2) There is NO registration form, because it is assumed that the chat participant will 'worry' about the existence of the account in advance (write to me, for example, through an anti-copywriter)
3) If a user logs in under the 'User' role, then he will have nothing except chat, there is a dropdown on the top right where there is a log out button
4) The most interesting thing is logging in under the 'Admin' role... the first window is a regular chat (admin_chat.html), I made it so that for users with the 'Admin' role in the dropdown there was another 'Users' button, where the window opens (admin_users.html) with user data (username, email) and actions on them --->
            1) change data - email, password, username (edit_user.html)
            2) block -> a modal window opens where you need 
                enter the time and reason for blocking (the user will have 
               the corresponding window where it will be written: reason 
               blocking, what time it was blocked, and a time report (in 
               depending on the blocking time)
            3) deleting the user (the corresponding window in the remote 
                there will be no user)
            4) adding a user (modal window)
            5) the administrator can make a regular user 
              administrator
            I'm thinking of adding actions to delete a message
What about the database... I used SQLAlchemy, user passwords are hashed
Looks like I haven't forgotten anything...
