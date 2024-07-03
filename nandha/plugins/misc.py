


import asyncio
import uuid
import os
import json

from aiohttp import FormData
from nandha import aiohttpsession as session, app
from nandha.helpers.decorator import command
from telegram import constants
from PIL import Image




@command('paste')
async def Paste(update, context):
   '''
   Purpose: 
        Paste code or text fike in dpaste.org for share.
   Requires:
        Reply to a t ext message o r text file. 
   Return:
        Paste link and raw link for of dpaste.org.
   '''
   
   message = update.message
   bot = context.bot
   reply = message.reply_to_message

   msg = await message.reply_text(
      "*⚡ Getting Link...*", parse_mode=constants.ParseMode.MARKDOWN
   )
   if reply and reply.document and reply.document.mime_type.startswith('text'):
       file = await (await bot.get_file(reply.document.file_id)).download_to_drive()
       with open(file, 'r') as f:
            content = f.read()
       os.remove(file)
   elif reply.text or reply.caption:
       content = reply.text or reply.caption
   else:
       return await msg.edit_text(
           text="*Reply to a text or text file document...*",
           parse_mode=constants.ParseMode.MARKDOWN
       )
      
   api_url = "https://dpaste.org/api/" 
   
   try:

      async with session.post(
            url=api_url,
            data={
                'format': 'json',
                'content': content,
                'lexer': 'python',
                'expires': '604800', #expire in week
            }, headers={'Content-Type': 'application/x-www-form-urlencoded'}
        ) as response:
             if response.status != 200:
                 return await msg.edit_text(f"❌ Error Status code: {response.status}")
             data = json.loads(await response.text())
             url = data.get('url')
             raw_url = url + '/raw'
             text = (
               f"⚡ *Paste View*:\n{url}"
               f"\n\n🌠 *Raw View*:\n{raw_url}"
             )
             return await msg.edit_text(
                  text=text, parse_mode=constants.ParseMode.MARKDOWN
             )

   except Exception as e:
        return await msg.edit_text(f"❌ Error: {str(e)}")

             








@command(('tm', 'tgm'))
async def Telegraph(update, context):
    '''
    Purpose:
       Get image/gif link for share and use it for many purpose.
    Requires:
       Reply to image or gif 
    Returns:
       Get a sharable link of media 
    '''
   
    message = update.message
    bot = context.bot

    api_url = "https://telegra.ph/upload"

    reply = message.reply_to_message
    if not reply:
        return await message.reply_text(
            text="⚡ Reply to the animation (GIF) or a photo to upload in graph.org"
        )
    
    if reply.photo:
        file_name = f"{str(uuid.uuid4())}.jpg"
        media_type = "image/jpg"
        file_id = reply.photo[-1].file_id
      
    elif reply.sticker:
        file_name = f"{str(uuid.uuid4())}.webp"
        media_type = "image/webp"
        file_id = reply.sticker.file_id
      
    elif reply.animation:
        file_name = reply.animation.file_name
        media_type = reply.animation.mime_type
        file_id = reply.animation.file_id
      
    else:
        return await message.reply_text(
            text="⚡ Reply to the animation (GIF) or a photo to upload in graph.org"
        )
    
    msg = await message.reply_text("Downloading...")
    file = await bot.get_file(file_id)
    file_path = await file.download_to_drive(
       custom_path=file_name
    )
    
    if reply.sticker:
        # Convert WebP sticker to JPG
        with Image.open(file_path) as img:
            img = img.convert("RGB")
            converted_file_name = f"{str(uuid.uuid4())}.jpg"
            converted_file_path = os.path.join(os.path.dirname(file_path), converted_file_name)
            img.save(converted_file_path, "JPEG")
            os.remove(file_path)  # Remove the original WebP file
            file_path = converted_file_path
            media_type = "image/jpg"
    
    with open(file_path, 'rb') as f:
        file_contents = f.read()
    
    form_data = FormData()
    form_data.add_field("file", file_contents, filename=os.path.basename(file_path), content_type=media_type)
    
    async with session.post(api_url, data=form_data) as response:
        os.remove(file_path)
        if response.status == 200:
            data = await response.json()
            if isinstance(data, dict):
                return await msg.edit_text("❌ problem while uploading file.")
            src = data[0].get('src')
            url = 'https://graph.org' + src
            return await msg.edit_text(url)
        else:
            return await msg.edit_text(
                text=f"❌ can't upload status code: {str(response.status)}"
  )
