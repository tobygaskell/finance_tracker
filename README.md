# finance_tracker

This will track the finances required to buy a house

```
docker build -t finances .
docker run -p 8501:8501 finances
docker tag finances tobygaskell/house-finances:latest
docker push tobygaskell/house-finances:latest
```

```
kubectl rollout restart deployment house-finances -n house
```
