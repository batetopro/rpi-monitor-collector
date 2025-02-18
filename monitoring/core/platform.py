import hashlib


from core.models import PlatformModel


class PlatformRegistry:
    @classmethod
    def get_or_create(cls, model, os_name, system, machine, processor,
                      platform):

        signature = hashlib.sha256(
            f'{model}@{os_name}@{system}@{machine}@{processor}@{platform}'
            .encode()
        ).hexdigest()

        entity = PlatformModel.objects.filter(signature=signature).first()
        if entity:
            return entity

        entity = PlatformModel(
            model=model,
            os_name=os_name,
            system=system,
            machine=machine,
            processor=processor,
            platform=platform,
            signature=signature
        )

        entity.save()

        return entity
