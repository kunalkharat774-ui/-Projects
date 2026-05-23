<?php

$correctUser = "admin";
$correctPass = "12345";

echo "Enter Username: ";
$user = trim(fgets(STDIN));

echo "Enter Password: ";
$pass = trim(fgets(STDIN));

echo "Enter Email Address: ";
$email = trim(fgets(STDIN));

echo "Enter Country: ";
$country = trim(fgets(STDIN));

echo "Enter Device Name: ";
$device = trim(fgets(STDIN));

$date = date("Y-m-d H:i:s");

echo "\n";

if($user == $correctUser && $pass == $correctPass){

    echo "Login Successful\n\n";

    echo "User Details:\n";
    echo "Username: $user\n";
    echo "Email: $email\n";
    echo "Country: $country\n";
    echo "Device Name: $device\n";
    echo "Login Date: $date\n";

} else {

    echo "Invalid Login";

}

?>
