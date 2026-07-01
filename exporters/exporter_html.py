from html import escape


def export_html(mails, filename):

    html = """
<html>
<head>
<meta charset="utf-8">

<style>

body{
font-family:Yu Gothic UI;
background:#f5f5f5;
}

.mail{
background:white;
padding:15px;
margin:10px;
border-radius:8px;
box-shadow:0 0 8px #ccc;
}

pre{
white-space:pre-wrap;
}

</style>

</head>

<body>

<h1>Mail Visualizer</h1>

"""

    for mail in mails:

        html += f"""

<div class="mail">

<h3>{escape(mail["subject"])}</h3>

<b>From</b><br>

{escape(mail["from"])}

<br><br>

<b>Date</b><br>

{escape(mail["date"])}

<hr>

<pre>{escape(mail["body"])}</pre>

</div>

"""

    html += "</body></html>"

    with open(filename,"w",encoding="utf-8") as f:
        f.write(html)