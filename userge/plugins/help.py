from userge import userge, Message


@userge.on_cmd("help", about="__to know how to use **USERGE** commands__")
async def helpme(message: Message):
    out, is_mdl_or_key = userge.get_help(message.input_str)
    cmd = message.input_str

    if not out:
        out_str = "__No Module or Command Found!__"

    elif isinstance(out, str):
        out_str = f"`{is_mdl_or_key}`\n\n{out}"

    elif isinstance(out, list) and is_mdl_or_key:
        out_str = """**--Which module you want ?--**

**Usage**:

    `.help [module_name]`

**Available Modules:**\n\n"""

        for i in out:
            out_str += f"    `{i}`\n"

    elif isinstance(out, list) and not is_mdl_or_key:
        out_str = f"""**--Which command you want ?--**

**Usage**:

    `.help .[command_name]`

**Available Commands Under `{cmd}` Module:**\n\n"""

        for i in out:
            out_str += f"    `{i}`\n"

    await message.edit(text=out_str, del_in=15)