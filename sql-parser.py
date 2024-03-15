import sqlparse
import tkinter as tk
from tkinter import filedialog
import os
import pyperclip
import chardet
import pandas as pd

print(os.getcwd())

# 获取读取文件的文件编码类型
def get_file_encoding(file_path):
    data = open(file_path,'rb').read()
    return chardet.detect(data)['encoding']

# 定义文件筛选器的类型（固定的，不随导入文件的变化而变化）
file_type_mapping = {
    'sql': ("SQL files", "*.sql"),
    'csv': ("CSV files", "*.csv"),
    'txt': ("TXT files", "*.txt"),
}

# 定义英文和日文的映射关系（固定的，不随导入文件的变化而变化）
token_mapping = {
    'SELECT': '検索項目: ',
    'FROM': '検索TBL: ',
    'WHERE': '条件: ',
    'INSERT': '追加: ',
    'UPDATE': '更新: '
    # 添加更多的映射关系...
}


def str_find_all(a, b):
    start = 0
    finds=[]
    while True:
        start = a.find(b, start)
        if start == -1:
            break
        finds.append(start)
        start += 1
    return finds

def get_txt_option_by_window(reference_excel_path):
    root = tk.Tk()
    root.geometry('800x500')
    root.title("帮你自动获取对应文件，而不用亲自写")

    # 选取据点Label
    site_label = tk.Label(root,text='请选取据点（下面这个按钮是下拉框，可以选取据点）')
    site_label.pack()

    # df=pd.read_excel(reference_excel_path)
    # 从 df 当中获取速度太慢了，定期维护下这个 site-id 的列表就好...
    site_id_list=(
                    "特殊特性",
                    "vave",
                    "q-net",
                    "ymc",
                    "ypmi",
                    "yejp",
                    "y-com_edi",
                    "yeid",
                    "ypmj",
                    "削除",
                    "stdca",
                    "ymmc",
                    "ympc",
                    "stdca_eng",
                    "rapras",
                    "std-ia",
                    "std-lg",
                    "ymec",
                    "mrp_common",
                    "g-pacos"
                )

    # 下拉框设置（pick_site_var=选取的值）
    pick_site_var = tk.StringVar()
    pick_site_var.set(site_id_list[3])
    site_box = tk.OptionMenu(root,pick_site_var,*site_id_list)
    site_box.pack()

    # 选取表名Label
    table_label = tk.Label(root,text='请输入TBL（如de_itemmast,de_itemcomn这种）；每个TBL使用英字逗号隔开')
    table_label.pack()
    table_label2 = tk.Label(root,text='（表别名的处理相对比较复杂【例如多次join同一张表时，这几张表不应该被翻译成同名，这个问题暂时没法解决，抱歉！】）')
    table_label2.pack()

    # 设置表名输入框
    pick_tables_var = tk.StringVar()
    entry = tk.Entry(root,font=('consolas',12),textvariable=pick_tables_var)
    entry.pack()

    mapping=dict()
    def on_confirm():
        site_id = pick_site_var.get()
        # tables  = pick_tables_var.get().split(",")
        tables  = entry.get().split(",")
        msg_box_feedback = tk.messagebox.askokcancel(title='信息展示',message="您的据点：{}\n您所选的表：\n{}\n确定吗？".format(site_id,',\n'.join(tables)))
        if msg_box_feedback == True:
            root.quit()
            root.destroy()
            print("表名已录入，解析中，时间很长，请稍等...")
            df=pd.read_excel(reference_excel_path)
            for db_table in tables:
                key_value_list=df.query(f'site_id == @site_id and db_table == @db_table')[['col_name','col_desc']].values.tolist()
                current_sites=[site_id]
                while len(key_value_list) == 0:
                    sites_strs=[]
                    for idx,site_id in enumerate(site_id_list,1):
                        sites_strs.append(f"据点编号：{idx}) -> {site_id}")
                    sites_strs_s=" \n".join(sites_strs)
                    other_site_idx_input = input("\n\n在据点【{}】下，未找到表{}的定义信息，请参考以下输入据点编号，选取另一个据点（建议ymc据点比较全）\n\n{}".format(", ".join(current_sites),db_table,sites_strs_s+'\n'))
                    if other_site_idx_input.isdigit():
                        if len(site_id_list) >= int(other_site_idx_input):
                            other_site=site_id_list[int(other_site_idx_input)-1]
                            key_value_list=df.query(f'site_id == @other_site and db_table == @db_table')[['col_name','col_desc']].values.tolist()
                            current_sites.append(other_site)
                        else:
                            print("数组长度越界，输入一个不长于据点列表长度的数字")
                    else:
                        print("非数字，重新输入")
                for key_value in key_value_list:
                    key,value=key_value
                    if key in mapping.keys() and value != mapping[key]:
                        ask=input("存在重复的字段Key且新旧值不相同: \"{}\"，请确认是否覆盖[直接回车表示确认覆盖，输入任意字符表示不覆盖]:\n\t先前取值为\"{}\"; \t当前取值为\"{}\";".format(key,mapping[key],value))
                        if ask == '':
                            mapping[key]=value
                            print("已覆盖先前字段")
                        else:
                            print("已选择不覆盖先前字段")
                            continue
                    else:
                        mapping[key]=value
                raw_table_name=df.query(f'site_id == @site_id and db_table == @db_table')['db_name'].values.tolist()[0]
                flag2=1
                while flag2:
                    ask2 = input("对于表{}，似乎没有解析出正确的表名，请手动输入正确的表名：\n\t（参考表名（也就是定义书的文件名）：{}）".format(db_table,raw_table_name))
                    if input("您输入的表名为：{}，确认是正确的表名吗？\n\t回车表示正确，任意键表示不正确：".format(ask2)) == "":
                        real_table_name=ask2
                        mapping[db_table]=real_table_name
                        print("表名已确认：{}\t->\t{}".format(db_table,real_table_name))
                        flag2=0
            # print('mapping:',mapping)

    # 完成输入，点确定按钮
    b3 = tk.Button(root,text='我已经输入了据点和所有相关表名，点确定',command=on_confirm)
    # b3.bind('<Button-1>',on_confirm)
    b3.pack()

    root.mainloop()#阻止窗口关闭（直到点确定关闭）

    # where不是token，这里要单独追加下
    mapping['where']='条件'
    return mapping

def get_sql_by_window():

    root = tk.Tk()
    root.title("请将SQL文粘贴在此处（必须是同一据点的SQL文）（多段SQL文用英字分号隔开）")

    sql_var = tk.StringVar()

    text = tk.Text(root,width=50,height=10,font=('consolas',12))
    text.grid(row=0,column=0,columnspan=3)

    b3 = tk.Button(root,text='获取数据')
    b3.grid(row=1,column=1)

    def update_var(*args):
        sql_var.set(text.get("0.0", 'end'))
        if len(sql_var.get()) > 0:
            root.quit()
            root.destroy()
        else:
            print("未获取到数据！")
    
    b3.bind('<Button-1>',update_var)

    # 点击获取数据，自动关闭窗口
    label = tk.Label(root, textvariable=sql_var)

    # print('pass: ',sql_var.get())
    
    root.mainloop()#阻止窗口关闭

    return sql_var.get()


def choose_dir_output():
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口

    folder_selected = filedialog.askdirectory(title="想要在哪个文件夹保存导出的文件呢？",initialdir="/")
    if folder_selected:
        print("选择的导出文件夹路径为:", folder_selected)
        return folder_selected
    else:
        print("未选择任何导出文件夹路径")

def choose_file_get_file_path(file_type):

    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口

    file_type_add = file_type_mapping[file_type]
    filetypelist=[]
    filetypelist.append(("All files", "*.*"))
    filetypelist.append(("TXT files", "*.txt"))
    filetypelist.append(file_type_add)
    

    file_path = filedialog.askopenfilename(title="选择{}文件".format(file_type.upper()), initialdir="/",filetypes=filetypelist)  # 弹出文件选择对话框

    if file_path:
        print("选择的文件路径为:", file_path)
        return file_path
    else:
        print("未选择任何文件")

# def get_table_mapping_from_file(file_path):
#     assert file_path
#     mapping = dict()
#     with open(file_path,'r',encoding=get_file_encoding(file_path)) as f:
#         lines = [line.replace("\n",'') for line in f.readlines() if line.replace("\n",'') != '']
#     for each_line in lines:
#         # tab和逗号混用都可以
#         if '\t' in each_line:
#             value,key=each_line.split("\t")
#         elif ',' in each_line:
#             value,key=each_line.split(",")
#         # 可能会复制大写或者大小写混输的key过来，必须保证引入的所有key都是小写的，
#         key=key.lower()
#         if key in mapping.keys() and mapping[key] != value:
#             ask=input("存在重复的字段Key且新旧值不相同: \"{}\"，请确认是否覆盖[直接回车表示确认覆盖，输入任意字符表示不覆盖]:\n\t先前取值为\"{}\"; \t当前取值为\"{}\";".format(key,mapping[key],value))
#             if ask == '':
#                 mapping[key]=value
#                 print("已覆盖先前字段")
#             else:
#                 print("已选择不覆盖先前字段")
#                 continue
#         else:
#             mapping[key]=value
#     print('mapping:',mapping)
#     return mapping

# token 转换为 日文
def map_token_to_jpn(token):
    if token.value.upper() in token_mapping:
        return token_mapping[token.value.upper()]
    return token.value

# table 转换为 日文（自己改了一点，不太严谨）
def map_table_to_jpn(identifier):
    if identifier.value.lower() in table_mapping:
        return table_mapping[identifier.value.lower()]
    if len(identifier.value.strip()) !=0:
        for k,v in table_mapping.items():
            # 防止把string的其他部分也lower了，只lower需要lower的部分
            finds=str_find_all(identifier.value.lower(),k)
            for find_idx in finds:
                new_str=identifier.value[0:find_idx]+identifier.value[find_idx:find_idx+len(k)].lower()+identifier.value[find_idx+len(k):]
                identifier.value = new_str
            identifier.value=identifier.value.replace(k,v)
    return identifier.value


# 设置导出文件夹

if input("选择：同意将【D盘根目录】为默认输出文件夹？手动选取输出文件夹？\n\t\t（直接回车为：\t同意将【D盘根目录】为默认输出文件夹；\n\t\t输入其他任意字符为：手动选取输出文件夹）") == '':
    # 选择：默认输出在D盘根目录
    output_dir="D:/"
else:
    # 选择：手动指定输出文件夹
    output_dir = choose_dir_output()

print("导出文件夹设置为：{}".format(output_dir))

# 读入SQL文
    
if input("选择：复制SQL文到随后打开的新窗口内？选取现有的SQL文件？\n\t\t（直接回车为：粘贴SQL文到新窗口；\n\t\t输入其他任意字符为：选取现有的SQL文件）") == '':
    # 选择：复制到新窗口
    sql=get_sql_by_window()
else:
    # 选择：读入现有SQL文
    sql_file = choose_file_get_file_path("sql")
    with open(sql_file,'r',encoding=get_file_encoding(sql_file)) as f:
        sql=f.read()

print("获取到的SQL文为：\n"+sql)

# 读入【对应关系】文件

print("【对应关系】文件的设置，已经有统一的步骤了：\n\n首先，请把\"【YNS全据点】表定义书导出汇总.xlsx\"放在与exe文件相同的路径下，不要修改文件名以免无法读入\n检测文件中：...")
reference_excel_path = os.getcwd()+os.sep+'【YNS全据点】表定义书导出汇总.xlsx'
flag = 0 if os.path.exists(reference_excel_path) == True else 1
while flag:
    if input("请再次确认是否存在xlsx文件：（放进去了就按回车，会自动检测）") == '' and os.path.exists(reference_excel_path):
        flag=0
table_mapping = get_txt_option_by_window(reference_excel_path)
print("获取到的对应关系为：\n")
for key,value in table_mapping.items():
    print(key,'\t->\t',value)

# 解析 SQL 语句

translated_sql_s_list=[]

for each_parsed in sqlparse.parse(sql):
    # 遍历 tokens 并进行映射
    translated_sql = []
    for item in each_parsed.tokens:
        if item.is_group:
            # 非token的那些数据（注意，where语句也是非token语句）
            translated_sql.append(' '.join(map(map_table_to_jpn, item.tokens)))
        else:
            # token语句，例如 select，from 这种
            translated_sql.append(map_token_to_jpn(item))
    # 输出映射后的 SQL
    translated_sql_s=' '.join(translated_sql)
    format_line="\n\n--******************************--\n\n"
    translated_sql_s=format_line+translated_sql_s+format_line
    translated_sql_s_list.append(translated_sql_s)

translated_sql_s_list_s="".join(translated_sql_s_list)

with open(output_dir+os.sep+"new-out-res.txt",'w',encoding="utf-8") as f:
    f.write(sql)
    f.write("\n\n--******************************--\n\n")
    f.write(translated_sql_s_list_s)

comp_sql='\n\n--******************************--\n\n'+sql+"\n\n--******************************--\n\n"+translated_sql_s_list_s
flag3=1
while flag3:
    ask=input("想要跟着英文SQL文一起粘贴，还是只要粘贴解析过的日文SQL？\n\t[1:日英都想要；2:只想要日文SQL]")
    if ask == '1':
        pyperclip.copy(comp_sql)
        flag3=0
    elif ask == '2':
        pyperclip.copy(translated_sql_s_list_s)
        flag3=0


print("导出完成！已写入: {}".format(output_dir+os.sep+"new-out-res.txt"))
print("\n（请注意：处于方便考虑，这些内容同时也写入了您的剪贴板，可以直接粘贴到vscode甚至是excel）")
print("\n（因开发周期较短及SQL方言问题，不可避免会出现转换错误的地方，请大家一定要再校对一两遍！）")

input("Press Any Key to exit…")

