export async function execute() {
  await new Promise((resolve) => setTimeout(resolve, 1000));
}

await execute();