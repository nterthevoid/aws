<html>
     <head>
         <title>Welcome</title>
     </head>
 <body style="color: #ffffff; background-color: #000000" >
     <p><img src="vault.png" width="500" height="300"></p>
    <p><?php echo "Destination host:".gethostname(); ?></p>
    <p><?php $ipaddress = getenv("REMOTE_ADDR") ; Echo "Source IP Address" . $ipaddress; ?></p>
    <video width="640" height="360" controls muted loop autoplay>
    <source src="Countdown.mp4" type="video/mp4">
    </video>
 </body>
</html>

