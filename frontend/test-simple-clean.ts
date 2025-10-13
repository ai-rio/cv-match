// Simple clean TypeScript test file
interface TestInterface {
  name: string;
  id: number;
}

function testFunction(item: TestInterface): string {
  return `Item: ${item.name} (ID: ${item.id})`;
}

const testItem: TestInterface = {
  name: 'Test Item',
  id: 123,
};

console.log(testFunction(testItem));
