#include <iostream>
using namespace std;

#include "./some_lib_dir/util.cpp"

int main() {
  int x, y;
  cin >> x >> y;
  int answer = util::add(x, y);
  cout << answer << endl;
  return 0;
}
