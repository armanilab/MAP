/*
 * Code for the magnetophotometer (MAP).
 * Header class for States
 * Written by: Lexie Scholtz
 *             Vic Nunez
 * Created: 2022.09.29
 * Last Updated: 2023.04.03
*/

enum States {
  ENTER_NAME = 0,
  ENTER_TIME,
  TEST_READY,
  TEST_IN_PROGRESS,
  TEST_ENDED,
  ERROR_LOGGER,
  ERROR_SENSOR,
  ERROR_BUTTON,
  NAME_OVERWRITE,
};
