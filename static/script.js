
function validate(unames)
{
    var name = document.getElementById("uname").value;
    var password = document.getElementById("pass").value;
    var alert = document.getElementById("msg");
    var successAlert = document.getElementById("success");
    // Clear success message if present
    successAlert.innerHTML = "";
    // want to perform these checks
    // the password should include at least one
    //upper case letter, one lower case letter, one digit and one of these symbols [+, !, *, -] and its length
    //should be at least ten.

    for (var i = 0; i < unames.length; i++)
    {
        if (unames[i] == name)
        {
            alert.innerHTML = "Username already exists";
            return false;
        }
    }

    if (password.length < 10)
    {
        alert.innerHTML = "Password should be at least 10 characters long";
        return false;
    }
    // using regex for password validation using the search method
    else if(password.search(/[a-z]/) == -1)
    {
        alert.innerHTML = "Password should have at least one lower case letter";
        return false;
    }
    else if(password.search(/[A-Z]/) == -1)
    {
        alert.innerHTML = "Password should have at least one upper case letter";
        return false;
    }
    else if(password.search(/[0-9]/) == -1)
    {
        alert.innerHTML = "Password should have at least one digit";
        return false;
    }
    else if(password.search(/[\+\!\*\-]/) == -1)
    {
        alert.innerHTML = "Password should have at least one of these symbols [+, !, *, -]";
        return false;
    }
    else
    {
        alert.innerHTML = "";
        return true;
    }

    return true;
}
