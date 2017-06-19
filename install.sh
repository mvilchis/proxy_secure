while getopts ":p:" opt; do
    case $opt in
        p) PROJECT_NAME="$OPTARG"
           ;;
        \?) echo "Opción inválida -$OPTARG" >&2
            ;;
    esac
done


git init ${PROJECT_NAME}

cd ${PROJECT_NAME}

git remote add "template" https://github.com/mvilchis/webhook-template.git

git pull template master

########## CHANGE KUBERNETES FILE  ##########

mv kubernetes/webhook_deployment.yaml  kubernetes/webhook_${PROJECT_NAME}_deployment.yaml
mv kubernetes/webhook_service.yaml  kubernetes/webhook_${PROJECT_NAME}_service.yaml
find ./kubernetes/ -type f -exec sed -i -e "s/-dummy/-${PROJECT_NAME}/g" {} \;

########## END KUBERNETES FILE  #########


echo ${PROJECT_NAME} > .project-name

git add .project-name ./kubernetes

git commit -m "Ajustando el nombre del proyecto a ${PROJECT_NAME}"

echo "############################################################################################"
echo "##                                                                                        ##"
echo "##  No olvides modificar los archivos utils y webhook con el codigo correspondiente       ##"
echo "##                                                                                        ##"
echo "############################################################################################"

echo ""
