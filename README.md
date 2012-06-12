django-filelibrary
==================

Generic file library for django. Allows for secure sending of files based on permissions. This is used on a few of our
projects and posted here for inspiration and reference; if interest builds then it will be turned into an official 
stand alone app. 

If you are going to use it in your project just include as a project module rather then a stand alone app. Doing so 
allows you to modify it according to your needs without having to do 'filelibrary_ext' app proxy. 

To prevent unauthorized access to your upload media folder you must include the following Apache directive:

```apache
   # Security - prevent direct apache serving of /media/filelibrary
   <Location /media/filelibrary/>
      Order deny,allow
      Deny from all
   </Location>
```