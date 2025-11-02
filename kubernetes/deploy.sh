kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f mongo.yaml
kubectl apply -f affichage.yaml
kubectl apply -f ajouter.yaml
kubectl apply -f auth.yaml
kubectl apply -f web.yaml
kubectl apply -f ingress.yaml


kubectl get all -n colis-app