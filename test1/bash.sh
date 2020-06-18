# param 1 = best/all
# param 2 = period/rating
# if param1 = all:
  # =без порога
  # =>10
  # =>25
  # =>50
  # =>100

# if param1 = best
  # =day
  # =week
  # =month
  # =year

curl -X GET '0.0.0.0:8000/task?category=all&period=без_порога&phrase=Python'