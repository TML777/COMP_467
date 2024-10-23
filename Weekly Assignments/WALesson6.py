import argparse


parser = argparse.ArgumentParser(description='Count lines in a text file.')
parser.add_argument('file', metavar='FILE', type=str,
                    help='path to the text file to be processed')
parser.add_argument('--verbose' , action='store_true', dest='long_verbose',
                    help='print each line to console')

args = parser.parse_args()


with open(args.file, 'r') as f:
    line_count = 0
    for line in f:
        if args.long_verbose:
            print(line.strip())

        line_count += 1

print("Total lines: " + str(line_count))


"""
tiko@Tikos-MacBook-Pro COMP 467 Code % python3 WALesson6.py WA6Text.txt --verbose
Hello, world!
This is a sample text file to test out Python code.
Chaja is an amazing prof.
More Chaja lore during class plz.
The quick brown fox jumps over the lazy dog.
Total lines: 5
tiko@Tikos-MacBook-Pro COMP 467 Code % python3 WALesson6.py WA6Text.txt          
Total lines: 5
"""