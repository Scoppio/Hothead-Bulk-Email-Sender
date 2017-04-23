<h1><img src="http://i.imgur.com/zw0ebQm.png" alt="Hothead" height=100px width=100px/>Hothead Email Sender with Sparkpost</h1>


[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=MDL5ECQGP38M6)

There was a day that I had to come up with a way to send thousands of emails to people subscribed to a service. Email sender softwares are usually very expensive, and their free version extremelly limited, so I decided to create my own with the skills I time I had in hands. 

This script is very crude, but have a few features:
- A/B test
- inline images
- personalization of emails
- html and text emails

All you need is a recipments list and you can create your own personalized email!

---

## How to template your emails

You can create html emails, or simple txt emails. But even if you want to send only html emails you MUST create a .txt counterpart to it, the script how it is now looks the code of the template emails and aquire the subject of the email ONLY inside the .txt email template, the plain text format is also good because many email providers only accept this kind of email, mainly those that are inside big companies (this is for safety measures)

## Peronsalization

You can add alot of stuff to personalize each email, but those things must be present inside the csv file or in the recipment list at sparkpost.
Look at the test.csv file which follows this script

---

## Why Sparkpost

It is connected to sparkpost because it is the only one that allows for a good amount of free emails each month, up to many thousands!!! It is by far the BEST bulk email service provider out there, with the better prices and best tools for visualizing how well it is doing!

---

## Donation
If this project help you save money or time to develop, **you can buy me a cup of coffee** :purple_heart:  

[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=MDL5ECQGP38M6)
