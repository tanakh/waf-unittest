#include <gtest/gtest.h>

#include "lib.h"

TEST(test, test)
{
  EXPECT_EQ(foo(123), 123+123);
}
