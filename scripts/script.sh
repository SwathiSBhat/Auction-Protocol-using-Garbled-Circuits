if [ $# != 3 ]; then
	echo -ne "bash script.sh <num_of_bidders> <proxy-port> <input-bid>\n"
	exit 1
fi

echo -ne "arg 1: $1\n"
echo -ne "arg 2: $2\n"
echo -ne "arg 3: $3\n"

for ((i=1; i<=$1; i++))
do
	echo -ne "$2\n$3\n" | python bidder-client.py
done

