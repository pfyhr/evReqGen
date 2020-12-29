
def output_json(csvfile):
    #this will be the ugliest workaround ever.
    data = np.genfromtxt(csvfile, skip_header=0)


if __name__ == "__main__":
    output_json('static/csv/leafRealData.csv')