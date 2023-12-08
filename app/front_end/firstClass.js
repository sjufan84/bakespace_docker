const numbers = [1, 2, 3, 4, 5];

for (let ii = 0; ii < numbers.length; ii++) {
  console.log(numbers[ii]);
}

const output = item => console.log(item);

numbers.forEach(output);