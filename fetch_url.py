import requests
import argparse
import yaml
import time

accumulated_dict = {}
max_latency = 500
delay = 15


def measure_response_time(url, headers, method, body):
    if method == "POST":
        response = requests.post(url, headers=headers, data=body)
    elif method == "PUT":
        response = requests.put(url, headers=headers, data=body)
    elif method == "DELETE":
        response = requests.delete(url, headers=headers, data=body)
    else:
        response = requests.get(url, headers=headers, data=body)

    response_time = response.elapsed.total_seconds() * 1000

    if 200 <= response.status_code < 300 and response_time <= max_latency:
        status = "UP"
    else:
        status = "DOWN"

    return status


def fetch_index_page(allowed_values, domain_count):
    counter = 0
    while True:
        count = {}
        counter += 1
        for item in allowed_values:

            try:
                headers = item.get('header', "")
                method = item.get('method', "")
                body = item.get('body', "")
                name = item.get('name')
                url = item.get('url')

                status = measure_response_time(url, headers, method, body)

                domain = url.split("/")[2]
                if status == "UP":
                    if domain in count:
                        count[domain] += 1
                    else:
                        count[domain] = 1
                else:
                    if domain in count:
                        count[domain] += 0
                    else:
                        count[domain] = 0

            except requests.RequestException as e:
                print(f"An error occurred: {e}")

        final_result = availability_percentage(count, counter, domain_count)

        for keys, values in final_result.items():
            print(f"{keys} has {values}% availability percentage")
        print("")

        time.sleep(delay)


def availability_percentage(count, counter, domain_count):
    result = {}
    for key, value in count.items():
        if key in domain_count:
            result[key] = round((value / domain_count[key]) * 100)

    for key, value in result.items():
        if key in accumulated_dict:
            accumulated_dict[key] += value
        else:
            accumulated_dict[key] = value

    divided_dict = {}
    for key, value in accumulated_dict.items():
        divided_dict[key] = round(value / counter)

    return divided_dict


def open_and_validate_file():
    domain_count = {}
    allowed_values = []
    parser = argparse.ArgumentParser()
    parser.add_argument('file')
    args = parser.parse_args()
    if args.file:
        with open(args.file, 'r') as file:
            data = yaml.load(file, Loader=yaml.SafeLoader)
    for item in data:
        if 'name' in item and 'url' in item:
            allowed_values.append(item)
        else:
            print("Skipping! name, url both must be passed :", item)

    for item in allowed_values:
        url = item['url']
        domain = url.split("/")[2]
        if domain in domain_count:
            domain_count[domain] += 1
        else:
            domain_count[domain] = 1

    return allowed_values, domain_count


def main():
    allowed_dict, count_domain = open_and_validate_file()
    fetch_index_page(allowed_dict, count_domain)


main()
