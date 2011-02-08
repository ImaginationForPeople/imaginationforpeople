<VirtualHost *:80>
    ServerName www.imaginationforpeople.com
    ServerAlias prod.imaginationforpeople.com imaginationforpeople.com

    WSGIProcessGroup webapp
    WSGIDaemonProcess webapp


    WSGIScriptAlias / /home/webapp/virtualenvs/prod.imaginationforpeople.com/imaginationforpeople/apache/prod.wsgi/

    <Location "/">
        Order Allow,Deny
        Allow from all
    </Location>


    <Directory /home/webapp/virtualenvs/prod.imaginationforpeople.com/imaginationforpeople/media/>
        Options -Indexes FollowSymLinks
    </Directory>

    <Location "/site_media">
        SetHandler None
    </Location>

    Alias /site_media /home/webapp/virtualenvs/prod.imaginationforpeople.com/imaginationforpeople/media/

    <Location "/admin_media">
        SetHandler None
        Options -Indexes FollowSymLinks
    </Location>

    Alias /admin_media /home/webapp/virtualenvs/prod.imaginationforpeople.com/lib/python2.6/site-packages/django/contrib/admin/media/

    ErrorLog /home/webapp/virtualenvs/prod.imaginationforpeople.com/logs/error.log
    LogLevel info
    CustomLog /home/webapp/virtualenvs/prod.imaginationforpeople.com/logs/access.log combined

</VirtualHost>


