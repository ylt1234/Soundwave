import subprocess
import argparse
import socket
import concurrent.futures
import queue
import csv
import os
from urllib.parse import urlparse
import tldextract
from colorama import init, Fore, Style

# 初始化 colorama
init(autoreset=True)

# 设置亮紫色
bright_purple = Style.BRIGHT + Fore.MAGENTA

# 解析命令行参数
parser = argparse.ArgumentParser(description='这是一个示例脚本，用于调用多个扫描模块并处理 -u 选项。')
parser.add_argument('-u', '--url', required=True, help='需要传递给扫描模块的URL')
args = parser.parse_args()
url = args.url

# 横幅
BANNER = r"""
                    ###### ###### #    # ###### #####  #    #   ##   #      # ######
                    #      #    # #    # #    # #    # #    #  #  #  #      # #
                    #      #    # #    # #    # #    # #    # #    #  #    #  #
                    ###### #    # #    # #    # #    # #    # ######  #    #  ######
                         # #    # #    # #    # #    # # ## # #    #   #  #   #
                         # #    # #    # #    # #    # ##  ## #    #   #  #   # 
                    ###### ######  ####  #    # #####  #    # #    #    ##    ######
"""
print(f"{bright_purple}+{BANNER}+{Style.RESET_ALL}")


# URL 转 IP 地址
def url_to_ip(url):
    try:
        parts = url.split('://')
        domain = parts[1].split('/')[0] if len(parts) > 1 else url
        return socket.gethostbyname(domain)
    except socket.gaierror:
        return None


# 端口扫描
def portScan(output_queue):
    tgtPorts =[
    '1', '5', '7', '9', '11', '13', '17', '19', '20', '21', '22', '23', '25', '26', '37', '42', '43', '49',
    '53', '67', '68', '69', '70', '79', '80', '88', '99', '101', '106', '107', '109', '110', '111', '113',
    '119', '123', '135', '137', '138', '139', '143', '161', '162', '179', '199', '201', '209', '210', '213',
    '220', '259', '389', '427', '443', '445', '464', '465', '500', '512', '513', '514', '515', '520', '587',
    '591', '593', '631', '636', '639', '646', '687', '691', '801', '808', '843', '873', '902', '981', '989',
    '990', '992', '993', '995', '1080', '1081', '1082', '1083', '1099', '1109', '1110', '1433', '1434',
    '1521', '1720', '1723', '1755', '1812', '1813', '1863', '2000', '2001', '2002', '2003', '2049', '2100',
    '2101', '2102', '2103', '2104', '2121', '2152', '2301', '2381', '2433', '2483', '2484', '2947', '3050',
    '3260', '3306', '3389', '3478', '3479', '3632', '3690', '4369', '4444', '4500', '4567', '4786', '4848',
    '5000', '5001', '5002', '5060', '5061', '5080', '5081', '5432', '5555', '5631', '5632', '5672', '5800',
    '5900', '5938', '5984', '6379', '6443', '6566', '6666', '6667', '7000', '7001', '7070', '7100', '7443',
    '7496', '7547', '7687', '7688', '7777', '8000', '8001', '8008', '8009', '8010', '8080', '8081', '8082',
    '8088', '8090', '8091', '8443', '8500', '8888', '9000', '9090', '9091', '9443', '9999', '10000', '11211',
    '27017', '27018', '50000', '50070'
]
    ip = url_to_ip(url)

    if not ip:
        output_queue.put("[-] 无法解析 URL 为 IP 地址")
        return

    result = []
    result.append(f"[+] Scan Results for: {ip}")
    for tgtPort in tgtPorts:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            sock.connect((ip, int(tgtPort)))
            result.append(f"[+] Port {tgtPort}/tcp open")
            sock.close()
        except:
            pass

    output_queue.put("\n".join(result))


# 目录扫描
def ScanDir(output_queue):
    command = ['python3', 'dirmap.py', '-i', url, '-lcf']
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    output_queue.put(stdout.decode('utf-8') if stdout else stderr.decode('utf-8'))


# 指纹识别
def FingerIdentify(output_queue):
    command = ['ehole_windows.exe', 'finger', '-u', url]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    output_queue.put(stdout.decode('utf-8') if stdout else stderr.decode('utf-8'))


# 子域名扫描
def ScanSubdomain(output_queue):
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    oneforall_path = os.path.join(current_script_dir, 'OneForAll', 'oneforall.py')
    command = ['python3', oneforall_path, '--target', url, 'run']
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    output_queue.put(stdout.decode('utf-8') if stdout else stderr.decode('utf-8'))


# 并行执行任务
def run_parallel_functions():
    # 为每个任务创建输出队列
    output_queue1 = queue.Queue()
    output_queue2 = queue.Queue()
    output_queue3 = queue.Queue()
    output_queue4 = queue.Queue()

    # 使用线程池并行执行任务
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.submit(portScan, output_queue1)
        executor.submit(ScanDir, output_queue2)
        executor.submit(FingerIdentify, output_queue3)
        executor.submit(ScanSubdomain, output_queue4)

    # 从队列中获取并打印结果
    result1 = output_queue1.get()
    result2 = output_queue2.get()
    result3 = output_queue3.get()
    result4 = output_queue4.get()

    print(f"{bright_purple}[端口扫描结果]:{Style.RESET_ALL}\n{result1}")
    print(f"{bright_purple}[后台扫描结果]:{Style.RESET_ALL}\n{result2}")
    print(f"{bright_purple}[指纹识别结果]:{Style.RESET_ALL}\n{result3}")
    print(f"{bright_purple}[子域名扫描结果]:{Style.RESET_ALL}\n")

    parsed_url = urlparse(url)
    netloc = parsed_url.netloc if parsed_url.netloc else url
    extracted = tldextract.extract(netloc)
    main_domain = f"{extracted.domain}.{extracted.suffix}"

    domain = main_domain

    csv_file_path = os.path.join('OneForAll', 'results', f'{domain}.csv')

    # 检查CSV文件是否存在
    if not os.path.exists(csv_file_path):
        print("没有找到子域名文件")
        print("全部扫描已经完成")
    else:
        with open(csv_file_path, mode='r', encoding='gbk') as file:
            subdomain_column_index = 4
            title_column_index = 14
            csv_reader = csv.reader(file)
            header = next(csv_reader)  # 跳过标题行
            for row in csv_reader:
                subdomain_column_value = row[subdomain_column_index]
                title_column_value = row[title_column_index]
                print(f"子域名：{subdomain_column_value}, 网址标题：{title_column_value}")

        print(f"{bright_purple}正在对子域名进行指纹识别和后台扫描：{Style.RESET_ALL}")
        with open(csv_file_path, mode='r', encoding='gbk') as file:
            csv_reader = csv.reader(file)  # 重新初始化csv_reader，
            _ = next(csv_reader)
            for row in csv_reader:
                subdomain_column_value = row[subdomain_column_index]


                def ScanDir1(subdomain, output_queue):
                    command = ['python3', 'dirmap.py', '-i', subdomain, '-lcf']
                    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    stdout, stderr = process.communicate()
                    output_queue.put(stdout.decode('utf-8') if stdout else stderr.decode('utf-8'))


                def FingerIdentify1(subdomain, output_queue):
                    command = ['ehole_windows.exe', 'finger', '-u', subdomain]
                    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    stdout, stderr = process.communicate()
                    output_queue.put(stdout.decode('utf-8') if stdout else stderr.decode('utf-8'))


                def run_parallel_tasks(subdomain):
                    output_queue1 = queue.Queue()
                    output_queue2 = queue.Queue()

                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        executor.submit(ScanDir1, subdomain, output_queue1)
                        executor.submit(FingerIdentify1, subdomain, output_queue2)

                    result1 = output_queue1.get()
                    result2 = output_queue2.get()

                    print(f"{bright_purple}对子域名{subdomain}后台扫描结果:{Style.RESET_ALL}\n{result1}")
                    print(f"{bright_purple}对子域名{subdomain}指纹识别结果:{Style.RESET_ALL}\n{result2}")


                run_parallel_tasks(subdomain_column_value)

# 主程序入口
if __name__ == "__main__":
    print(f"{bright_purple}开始端口扫描、后台扫描、指纹识别、子域名扫描：{Style.RESET_ALL}\n")
    run_parallel_functions()
