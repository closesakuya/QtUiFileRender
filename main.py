import os

try:
    import click
    import bs4
except ModuleNotFoundError:
    os.system("pip3 install click")
    os.system("pip3 install bs4")

import render


def get_valid_dir_name(dir_input: str):
    if not dir_input:  # 当前目录下创建文件夹
        ret = os.getcwd() + os.sep + "render_result"
        try:
            os.makedirs(os.getcwd() + os.sep + "render_result")
        except FileExistsError:
            pass
        return ret
    if not os.path.exists(dir_input):
        os.makedirs(dir_input)
        return dir_input

    return dir_input


def yield_all_ui(dir_name: str):
    for item in os.listdir(dir_name):
        if os.path.isdir(item):
            for sub_item in yield_all_ui(item):
                yield sub_item
        elif os.path.isfile(item):
            if os.path.splitext(item)[1] == ".ui":
                yield item
        else:
            # print("not support type, ", item)
            pass


@click.command()
@click.option('--file_name', prompt='import your file_name to render')
@click.option('--stylesheet', default="rander_strategy_01.py", help='your stylesheet(.py file) use to render')
@click.option('--output', default="", help='where to output you result')
def renderfile(file_name: str, stylesheet: str, output: str):
    click.echo('render a file : {0} use stylesheet: {1}'.format(file_name, stylesheet))
    assert os.path.isfile(file_name)
    assert os.path.isfile(stylesheet)

    if not output:
        click.echo('not input --output: use default cwd: {0}'.format(os.getcwd()))
        output = os.getcwd()
    output_file = ""
    if os.path.isdir(output):
        if not os.path.exists(output):
            os.makedirs(output)
        f1 = os.path.split(file_name)[1]
        # 防止覆盖
        if os.path.exists(output + os.sep + f1):
            output_file = output + os.sep + os.path.splitext(f1)[0] + "_result" + os.path.splitext(f1)[1]
        else:
            output_file = output + os.sep + f1
    elif os.path.isfile(output):
        output_file = output

    rd = render.Render(stylesheet)
    rd.do_render(src=file_name, dst=output_file)


@click.command()
@click.option('--file_dir', prompt='import your files_dir to render, '
                                   'will render all .ui files in this dir')
@click.option('--stylesheet', default="rander_strategy_01.py", help='your stylesheet(.py file) use to render')
@click.option('--output', default="", help='where to output you result')
def renderall(file_dir: str, stylesheet: str, output: str):
    click.echo("render all files in : {0} use stylesheet: {1}".format(file_dir, stylesheet))
    assert os.path.isdir(file_dir)
    assert os.path.isfile(stylesheet)
    output = get_valid_dir_name(output)
    rd = render.Render(stylesheet)
    gen = yield_all_ui(file_dir)
    for idx, item in enumerate(gen):
        if rd.do_render(src=item, dst=output + os.sep + os.path.split(item)[1]):
            click.echo("success({0})!".format(idx + 1))


if __name__ == "__main__":
    @click.group()
    def main():
        pass
    main.add_command(renderfile)
    main.add_command(renderall)
    main()
